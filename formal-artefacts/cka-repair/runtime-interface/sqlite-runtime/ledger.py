"""Trusted single-operation executor. Effects stay inside the same database.

The HTTP boundary is in ingress.py. Calling this module or modifying its
database already requires executor authority. No remote effect is performed.
"""
from pathlib import Path
import sqlite3


def validate_request(body):
    if type(body) is not dict or type(body.get("command")) is not str:
        raise ValueError("expected a command object")
    command = body["command"]
    fields = {"Submit": {"operation", "delta"}, "Service": set(),
              "SetPermission": {"value"}, "Advice": {"value"},
              "LostAck": set(), "Poll": set()}
    if command not in fields or set(body) != fields[command] | {"command"}:
        raise ValueError("unexpected or missing fields")
    if command in {"Advice", "SetPermission"} and type(body["value"]) is not bool:
        raise ValueError("value must be a boolean")
    if command == "Submit":
        op, delta = body["operation"], body["delta"]
        if type(op) is not str or not 1 <= len(op) <= 128 or not op.isascii():
            raise ValueError("operation must be a nonempty ASCII identifier")
        if type(delta) is not int or not -10**9 <= delta <= 10**9:
            raise ValueError("delta must be a bounded integer")
    return command, {key: body[key] for key in fields[command]}


class Ledger:
    def __init__(self, path):
        self.path = Path(path)

    def connect(self):
        con = sqlite3.connect(self.path, isolation_level=None, timeout=3)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA synchronous=EXTRA")
        con.execute("PRAGMA foreign_keys=ON")
        if con.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
            con.close()
            raise RuntimeError("this experiment requires rollback DELETE mode")
        return con

    def initialize(self):
        con = self.connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            con.execute("""CREATE TABLE IF NOT EXISTS state (
                id INTEGER PRIMARY KEY CHECK(id=1),
                permitted INTEGER NOT NULL CHECK(permitted IN (0,1)),
                stage TEXT NOT NULL CHECK(stage IN ('Idle','Pending','Approved','Completed')),
                advice INTEGER NOT NULL CHECK(advice IN (0,1)),
                operation TEXT, delta INTEGER,
                CHECK ((stage='Idle' AND operation IS NULL AND delta IS NULL) OR
                       (stage!='Idle' AND operation IS NOT NULL AND delta IS NOT NULL)))""")
            con.execute("CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY CHECK(id=1), balance INTEGER NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS effects (operation TEXT PRIMARY KEY NOT NULL, delta INTEGER NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, event INTEGER NOT NULL)")
            con.execute("INSERT OR IGNORE INTO state VALUES (1,1,'Idle',0,NULL,NULL)")
            con.execute("INSERT OR IGNORE INTO account VALUES (1,0)")
            con.execute("COMMIT")
        finally:
            con.close()

    def apply(self, command, *, checkpoint=None, **arguments):
        command, arguments = validate_request({"command": command, **arguments})
        visit = checkpoint or (lambda point: None)
        con = self.connect()
        try:
            visit("before_begin")
            con.execute("BEGIN IMMEDIATE")
            s = dict(con.execute("SELECT * FROM state WHERE id=1").fetchone())
            visit("after_read")
            event = {"Submit": 10, "Service": 11, "LostAck": 16, "Poll": 17}.get(command)
            if command == "Submit":
                if s["stage"] == "Idle":
                    s.update(stage="Pending", **arguments)
                elif (s["operation"], s["delta"]) != (arguments["operation"], arguments["delta"]):
                    raise ValueError("database is bound to a different operation or payload")
            elif command == "Service":
                if s["stage"] == "Pending" and s["permitted"]:
                    s["stage"] = "Approved"
                elif s["stage"] == "Approved" and s["permitted"]:
                    con.execute("INSERT INTO effects VALUES (?,?)", (s["operation"], s["delta"]))
                    con.execute("UPDATE account SET balance=balance+? WHERE id=1", (s["delta"],))
                    visit("after_effect")
                    s["stage"], event = "Completed", 1
            elif command == "SetPermission":
                s["permitted"] = int(arguments["value"])
                event = 2 + s["permitted"]
            elif command == "Advice":
                s["advice"] = int(arguments["value"])
                event = 14 + s["advice"]
            con.execute("UPDATE state SET permitted=?,stage=?,advice=?,operation=?,delta=? WHERE id=1",
                        (s["permitted"], s["stage"], s["advice"], s["operation"], s["delta"]))
            con.execute("INSERT INTO events(event) VALUES (?)", (event,))
            visit("after_state")
            con.execute("COMMIT")
            visit("after_commit")
            return {"event": event, "stage": s["stage"]}
        except BaseException:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
        finally:
            con.close()

    def snapshot(self):
        con = self.connect()
        try:
            con.execute("BEGIN")
            s = dict(con.execute("SELECT * FROM state WHERE id=1").fetchone())
            s["balance"] = con.execute("SELECT balance FROM account WHERE id=1").fetchone()[0]
            s["effects"] = [dict(r) for r in con.execute("SELECT * FROM effects ORDER BY operation")]
            s["events"] = [dict(r) for r in con.execute("SELECT * FROM events ORDER BY seq")]
            con.execute("COMMIT")
            return s
        finally:
            con.close()
