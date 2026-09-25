"""Behavioral tests. Uses real files, HTTP sockets and child processes."""
import csv
from contextlib import closing
import http.client
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from ledger import Ledger

HERE = Path(__file__).resolve().parent
OBSERVATIONS = {}


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sqlite-runtime-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.db"
        self.ledger = Ledger(self.path)
        self.ledger.initialize()

    def approved(self):
        self.ledger.apply("Submit", operation="op-1", delta=7)
        self.ledger.apply("Service")

    def consistent(self, ledger=None):
        s = (ledger or self.ledger).snapshot()
        self.assertEqual(s["balance"], sum(e["delta"] for e in s["effects"]))
        self.assertEqual(len(s["effects"]), int(s["stage"] == "Completed"))
        self.assertLessEqual(len(s["effects"]), 1)
        if s["effects"]:
            self.assertEqual(s["effects"][0]["operation"], s["operation"])
            self.assertEqual(s["effects"][0]["delta"], s["delta"])
        return s

    def test_advice_outage_and_retry(self):
        self.approved()
        self.ledger.apply("Advice", value=False)
        self.assertEqual(self.ledger.apply("Service")["event"], 1)
        self.ledger.apply("LostAck")
        self.ledger.apply("Submit", operation="op-1", delta=7)
        self.ledger.apply("Service")
        self.ledger.initialize()
        s = self.consistent()
        self.assertEqual((s["stage"], s["balance"]), ("Completed", 7))

    def test_revocation_at_commit(self):
        self.approved()
        self.ledger.apply("SetPermission", value=False)
        self.assertNotEqual(self.ledger.apply("Service")["event"], 1)
        self.assertEqual(self.consistent()["balance"], 0)
        self.ledger.apply("SetPermission", value=True)
        self.ledger.apply("Service")
        self.assertEqual(self.consistent()["balance"], 7)

    def test_operation_binding(self):
        self.approved()
        for op, delta in [("op-1", 8), ("op-2", 7)]:
            before = self.ledger.snapshot()
            with self.assertRaises(ValueError):
                self.ledger.apply("Submit", operation=op, delta=delta)
            self.assertEqual(before, self.ledger.snapshot())

    def test_generated_model_table(self):
        phases = ["Idle", "Pending", "Approved", "Completed"]
        commands = [("Submit", {"operation": "op-1", "delta": 7}),
                    ("Service", {}), ("SetPermission", {"value": False}),
                    ("SetPermission", {"value": True}), ("Advice", {"value": False}),
                    ("Advice", {"value": True}), ("LostAck", {}), ("Poll", {})]
        with (HERE.parent / "evidence/transition_table.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        checked = []
        for row in (r for r in rows if r["profile"] == "guarded"):
            state, command = int(row["state"]), int(row["command"])
            ledger = Ledger(Path(self.temp.name) / f"model-{state}-{command}.db")
            ledger.initialize()
            phase = phases[state // 4]
            # Fixtures cover the finite abstract state space; never used by HTTP.
            with closing(sqlite3.connect(ledger.path)) as con, con:
                con.execute("UPDATE state SET permitted=?, stage=?, advice=?, operation=?, delta=?",
                            ((state // 2) % 2, phase, state % 2,
                             None if phase == "Idle" else "op-1", None if phase == "Idle" else 7))
                if phase == "Completed":
                    con.execute("INSERT INTO effects VALUES ('op-1', 7)")
                    con.execute("UPDATE account SET balance=7")
            actual = ledger.apply(commands[command][0], **commands[command][1])
            s = self.consistent(ledger)
            target = 4 * phases.index(s["stage"]) + 2 * s["permitted"] + s["advice"]
            self.assertEqual((target, actual["event"]), (int(row["target"]), int(row["event"])), row)
            checked.append({"state": state, "command": command, "target": target, "event": actual["event"]})
        self.assertEqual(len(checked), 128)
        OBSERVATIONS["model_table"] = checked

    def child(self, action, *extra):
        return subprocess.run([sys.executable, "-B", str(HERE / "crash_worker.py"),
                               str(self.path), action, *extra], capture_output=True, text=True, timeout=20)

    def test_crash_recovery(self):
        records = []
        OBSERVATIONS["crash_recovery"] = records
        for point in ["before_begin", "after_read", "after_effect", "after_state", "after_commit"]:
            with self.subTest(point=point):
                self.path = Path(self.temp.name) / f"crash-{point}.db"
                self.ledger = Ledger(self.path)
                self.ledger.initialize()
                self.approved()
                result = self.child("crash", point)
                self.assertEqual(result.returncode, 73, result.stderr)
                recovered = self.child("snapshot")
                self.assertEqual(recovered.returncode, 0, recovered.stderr)
                before = json.loads(recovered.stdout)
                observation = {"point": point, "exit": result.returncode,
                               "recovered_stage": before["stage"], "recovered_balance": before["balance"],
                               "recovered_effects": len(before["effects"])}
                records.append(observation)
                committed = point == "after_commit"
                self.assertEqual(before["balance"], 7 if committed else 0)
                self.assertEqual(before["stage"], "Completed" if committed else "Approved")
                retry = self.child("service")
                self.assertEqual(retry.returncode, 0, retry.stderr)
                final = self.consistent()
                self.assertEqual((final["stage"], final["balance"]), ("Completed", 7))
                self.assertEqual(sum(e["event"] == 1 for e in final["events"]), 1)
                observation["after_retry_balance"] = final["balance"]

    def test_two_processes_same_operation(self):
        self.approved()
        gate = Path(self.temp.name) / "release"
        procs = [subprocess.Popen([sys.executable, "-B", str(HERE / "crash_worker.py"),
                                  str(self.path), "wait_service", str(gate)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        try:
            deadline = time.monotonic() + 10
            while len(list(gate.parent.glob("release.*.ready"))) != 2:
                if time.monotonic() >= deadline:
                    self.fail("both worker processes must be ready before release")
                time.sleep(0.01)
            gate.touch()
            results = [p.communicate(timeout=20) for p in procs]
            self.assertEqual([p.returncode for p in procs], [0, 0], results)
            s = self.consistent()
            self.assertEqual(s["balance"], 7)
            self.assertEqual(sum(e["event"] == 1 for e in s["events"]), 1)
            OBSERVATIONS["concurrent_submit"] = {"return_codes": [p.returncode for p in procs],
                                                 "balance": s["balance"], "effects": len(s["effects"])}
        finally:
            for p in procs:
                if p.poll() is None:
                    p.kill()
                    p.communicate(timeout=10)

    def test_revocation_serialized_while_service_holds_lock(self):
        self.approved()
        acquired, release, attempting, revoked = (threading.Event() for _ in range(4))
        errors = []

        def pause(point):
            if point == "after_read":
                acquired.set()
                if not release.wait(5):
                    raise TimeoutError("test did not release transaction")

        def service():
            try:
                self.ledger.apply("Service", checkpoint=pause)
            except Exception as e:
                errors.append(repr(e))

        def revoke():
            try:
                attempting.set()
                self.ledger.apply("SetPermission", value=False)
                revoked.set()
            except Exception as e:
                errors.append(repr(e))

        t1, t2 = threading.Thread(target=service), threading.Thread(target=revoke)
        t1.start()
        try:
            self.assertTrue(acquired.wait(5))
            t2.start()
            self.assertTrue(attempting.wait(5))
            self.assertFalse(revoked.wait(0.1))
        finally:
            release.set()
            t1.join(10)
            if t2.ident is not None:
                t2.join(10)
        self.assertFalse(t1.is_alive() or t2.is_alive())
        self.assertEqual(errors, [])
        self.assertTrue(revoked.is_set())
        s = self.consistent()
        self.assertEqual([e["event"] for e in s["events"]][-2:], [1, 2])
        OBSERVATIONS["serialized_revoke"] = {"last_events": [1, 2], "final_permission": s["permitted"]}

    def start_http(self):
        from ingress import make_server
        self.control, self.advice = secrets.token_hex(32), secrets.token_hex(32)
        server = make_server(self.ledger, self.control, self.advice)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02})
        thread.start()
        self.port = server.server_port

        def close():
            server.shutdown()
            server.server_close()
            thread.join(5)

        self.addCleanup(close)

    def request(self, token, payload):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        con = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            con.request("POST", "/command", body,
                        {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
            response = con.getresponse()
            return response.status, json.loads(response.read())
        finally:
            con.close()

    def test_http_authority_isolation(self):
        self.start_http()
        before = self.ledger.snapshot()
        self.assertEqual(self.request("invalid", {"command": "SetPermission", "value": False})[0], 401)
        for command in [{"command": "SetPermission", "value": False}, {"command": "Service"},
                        {"command": "Submit", "operation": "op-1", "delta": 7}, {"command": "Poll"}]:
            self.assertEqual(self.request(self.advice, command)[0], 403)
        self.assertEqual(self.request(self.advice, {"command": "Advice", "value": True, "role": "control"})[0], 400)
        self.assertEqual(before, self.ledger.snapshot())
        self.assertEqual(self.request(self.advice, {"command": "Advice", "value": True})[0], 200)
        for command in [{"command": "Submit", "operation": "op-1", "delta": 7},
                        {"command": "Service"}, {"command": "Service"}]:
            self.assertEqual(self.request(self.control, command)[0], 200)
        self.assertEqual(self.consistent()["balance"], 7)
        OBSERVATIONS["http"] = {"transport": "loopback HTTP", "unknown_token": 401,
                                "advice_control_attempts": [403] * 4, "role_field_injection": 400,
                                "advice_message": 200, "authorized_effect": 7}

    def test_http_rejects_ambiguous_inputs(self):
        self.start_http()
        before = self.ledger.snapshot()
        for payload in [b'{"command":"Advice","command":"Service","value":true}',
                        {"command": "Advice", "value": 1}, {"command": "SetPermission", "value": "false"},
                        {"command": "Submit", "operation": "op-1", "delta": True},
                        {"command": "Submit", "operation": "op-1", "delta": 2**63},
                        {"command": "Submit", "operation": "", "delta": 7},
                        {"command": "Service", "checkpoint": "after_effect"}, [], b'\xff']:
            self.assertEqual(self.request(self.control, payload)[0], 400, payload)
        self.assertEqual(before, self.ledger.snapshot())


if __name__ == "__main__":
    program = unittest.main(exit=False, verbosity=2)
    destination = os.environ.get("RUNTIME_AUDIT_OUTPUT")
    if destination:
        Path(destination).write_text(json.dumps({"tests_run": program.result.testsRun,
                                               "failures": len(program.result.failures),
                                               "errors": len(program.result.errors),
                                               "observations": OBSERVATIONS}, indent=2) + "\n", encoding="utf-8")
    sys.exit(0 if program.result.wasSuccessful() else 1)
