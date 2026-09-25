"""Run the real prototype and isolated negative controls; record exact evidence."""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_test(directory, evidence, label, selection=None):
    argv = [sys.executable, "-B", "-X", "utf8", str(directory / "test_runtime.py")]
    if selection:
        argv.append("RuntimeTests." + selection)
    destination = evidence / (label + ".json")
    env = os.environ.copy()
    env["RUNTIME_AUDIT_OUTPUT"] = str(destination)
    before = {p.name: sha(p) for p in directory.glob("*.py")}
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(argv, capture_output=True, env=env, timeout=60)
    log = evidence / (label + ".txt")
    log.write_bytes(result.stdout + result.stderr)
    assert before == {p.name: sha(p) for p in directory.glob("*.py")}
    record = {"command_argv": argv, "started_utc": started,
              "finished_utc": datetime.now(timezone.utc).isoformat(),
              "return_code": result.returncode, "source_sha256_before": before,
              "log_sha256": sha(log), "result_sha256": sha(destination)}
    return record, json.loads(destination.read_text())


def main():
    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    record, results = run_test(HERE, evidence, "tests")
    if record["return_code"] != 0 or results["failures"] or results["errors"]:
        print((evidence / "tests.txt").read_text(), end="")
        raise SystemExit("baseline failed; no success report issued")
    mutations = [
        ("authority_bypass", "ingress.py", 'if role == "advice" and command != "Advice":',
         'if False:  # Deliberately omit the advice authority restriction.',
         "test_http_authority_isolation"),
        ("cached_permission", "ledger.py", 'elif s["stage"] == "Approved" and s["permitted"]:',
         'elif s["stage"] == "Approved":  # Deliberately use stale approval.',
         "test_revocation_at_commit"),
        ("split_transaction", "ledger.py", '                    visit("after_effect")',
         '                    con.execute("COMMIT")\n                    con.execute("BEGIN IMMEDIATE")\n                    visit("after_effect")',
         "test_crash_recovery"),
    ]
    mutation_records = []
    for name, filename, old, new, selection in mutations:
        with tempfile.TemporaryDirectory(prefix="runtime-mutant-") as task_dir:
            target = Path(task_dir)
            for source in HERE.glob("*.py"):
                shutil.copyfile(source, target / source.name)
            source = target / filename
            content = source.read_text(encoding="utf-8")
            assert content.count(old) == 1, (name, "mutation anchor must be unique")
            source.write_text(content.replace(old, new), encoding="utf-8")
            observed, checks = run_test(target, evidence, "mutant-" + name, selection)
            detected = observed["return_code"] == 1 and checks["failures"] > 0 and checks["errors"] == 0
            mutation_records.append({"name": name, "file": filename, "replace": old, "with": new,
                                     "detected_by_assertion": detected, "run": observed})
            if not detected:
                raise SystemExit(f"negative control {name} did not produce the expected assertion failure")
    from ledger import Ledger
    with tempfile.TemporaryDirectory(prefix="runtime-settings-") as task_dir:
        ledger = Ledger(Path(task_dir) / "settings.db")
        ledger.initialize()
        with closing(ledger.connect()) as con:
            settings = {key: con.execute("PRAGMA " + key).fetchone()[0]
                        for key in ["journal_mode", "synchronous", "foreign_keys", "busy_timeout", "integrity_check"]}
    report = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "sqlite": sqlite3.sqlite_version, "platform": platform.platform(),
              "sqlite_settings_observed": settings, "baseline": record, "mutations": mutation_records,
              "model_inputs_sha256": {p.relative_to(HERE.parent).as_posix(): sha(p) for p in
                                     [HERE.parent / "Runtime_Interface.thy", HERE.parent / "emit_table.ML",
                                      HERE.parent / "evidence/runtime_interface.ML", HERE.parent / "evidence/transition_table.csv",
                                      HERE.parent / "evidence/run_record.json"]},
              "scope": ["Empirical Python/SQLite correspondence, not a new Isabelle proof",
                        "Single operation and same-database effects; not remote exactly-once",
                        "Abrupt application exits at five checkpoints; not power-loss or pager fault testing",
                        "Authenticated loopback request cases; assumes secret control token and protected executor/database",
                        "Finite concurrency scenarios; no deployed scheduling/fairness guarantee"]}
    (evidence / "run_record.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tests_run": results["tests_run"], "failures": results["failures"], "errors": results["errors"],
                      "model_transitions": len(results["observations"]["model_table"]),
                      "crash_points": len(results["observations"]["crash_recovery"]),
                      "mutations_detected": len(mutation_records), "sqlite": sqlite3.sqlite_version}, indent=2))


if __name__ == "__main__":
    main()
