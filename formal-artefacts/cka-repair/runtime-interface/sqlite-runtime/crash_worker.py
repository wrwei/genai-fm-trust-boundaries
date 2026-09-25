"""Fault-injection child process; never reachable from the HTTP request body."""
import json
import os
from pathlib import Path
import sys
import time

from ledger import Ledger


if __name__ == "__main__":
    ledger = Ledger(sys.argv[1])
    action = sys.argv[2]
    if action == "snapshot":
        print(json.dumps(ledger.snapshot()))
    elif action in {"service", "wait_service"}:
        if action == "wait_service":
            gate = Path(sys.argv[3])
            gate.with_name(gate.name + "." + str(os.getpid()) + ".ready").touch()
            deadline = time.monotonic() + 10
            while not gate.exists():
                if time.monotonic() >= deadline:
                    raise TimeoutError("parent did not release gate")
                time.sleep(0.01)
        print(json.dumps(ledger.apply("Service")))
    elif action == "crash":
        def checkpoint(point):
            if point == sys.argv[3]:
                os._exit(73)  # No connection cleanup, finally or rollback runs.
        ledger.apply("Service", checkpoint=checkpoint)
        raise RuntimeError("crash point was not reached")
    else:
        raise ValueError("unknown worker action")
