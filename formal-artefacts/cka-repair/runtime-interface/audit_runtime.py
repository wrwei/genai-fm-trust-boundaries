"""Audit the complete finite transition table emitted by generated SML.

No independently hand-transcribed runtime implementation is used. This audit
checks the exported executable and its serializer against a small reference
relation, and searches its finite graph for mutation counterexamples.
"""
from collections import deque
import csv
import hashlib
import json
from pathlib import Path
import sys

COMMANDS = ["Submit", "Service", "Revoke", "Restore", "AdviceUnavailable",
            "AdviceAvailable", "LostAck", "Poll"]
PROFILES = ["guarded", "cached", "advice_blocked", "retry"]
INITIAL = 2  # Idle, permission true, advice unavailable


def abstract(state):
    return bool((state % 4) // 2), state // 4 == 3


def find_witness(table, violation):
    queue = deque([(INITIAL, 0, [])])
    seen = {(INITIAL, 0)}
    while queue:
        state, effects, path = queue.popleft()
        for command in range(8):
            target, event = table[state, command]
            next_effects = effects + (event == 1)
            next_path = path + [command]
            if violation(state, effects, target, event):
                return {"commands": [COMMANDS[c] for c in next_path],
                        "length": len(next_path), "state_before": state,
                        "state_after": target, "event": event,
                        "search": "breadth-first over the reachable finite product graph"}
            item = target, min(next_effects, 2)
            if item not in seen:
                seen.add(item)
                queue.append((target, item[1], next_path))
    return None


def audit(path):
    tables = {profile: {} for profile in PROFILES}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            profile = row["profile"]
            state, command, target, event = (int(row[k]) for k in
                                            ["state", "command", "target", "event"])
            assert profile in tables and 0 <= state < 16 and 0 <= command < 8
            assert 0 <= target < 16
            assert event in [1, 2, 3, *range(10, 18)]
            assert (state, command) not in tables[profile]
            tables[profile][state, command] = target, event
    assert all(len(t) == 128 for t in tables.values())

    results = {}
    for profile, table in tables.items():
        failures = []
        for (state, command), (target, event) in table.items():
            permitted, completed = abstract(state)
            if event == 1:
                valid = permitted and not completed and abstract(target) == (permitted, True)
            elif event in (2, 3):
                valid = abstract(target) == (event == 3, completed)
            else:
                valid = abstract(target) == abstract(state)
            if not valid:
                failures.append({"state": state, "command": COMMANDS[command],
                                 "target": target, "event": event})

        def execute(commands):
            state, visible = INITIAL, []
            for c in commands:
                state, event = table[state, c]
                if event < 10:
                    visible.append(event)
            return state, visible

        stale = execute([0, 1, 2, 1])
        lost_ack = execute([0, 1, 1, 6, 0, 1])
        outage = execute([0, 1, 4, 1])
        results[profile] = {
            "transitions_checked": len(table),
            "one_step_reference_failures": failures,
            "unauthorised_effect_witness": find_witness(
                table, lambda s, n, t, e: e == 1 and not abstract(s)[0]),
            "duplicate_effect_witness": find_witness(
                table, lambda s, n, t, e: e == 1 and n >= 1),
            "revocation_scenario": {"final_state": stale[0], "visible_events": stale[1]},
            "lost_ack_scenario": {"final_state": lost_ack[0], "visible_events": lost_ack[1]},
            "advice_outage_scenario": {"final_state": outage[0],
                                       "completed": abstract(outage[0])[1]},
        }

    guarded = results["guarded"]
    assert not guarded["one_step_reference_failures"]
    assert guarded["unauthorised_effect_witness"] is None
    assert guarded["duplicate_effect_witness"] is None
    assert guarded["revocation_scenario"]["visible_events"] == [2]
    assert guarded["lost_ack_scenario"]["visible_events"] == [1]
    assert guarded["advice_outage_scenario"]["completed"]
    assert results["cached"]["unauthorised_effect_witness"] is not None
    assert results["retry"]["duplicate_effect_witness"] is not None
    assert not results["advice_blocked"]["one_step_reference_failures"]
    assert not results["advice_blocked"]["advice_outage_scenario"]["completed"]

    return {
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "state_encoding": "4*phase + 2*permission + advice_available; phases Idle/Pending/Approved/Completed = 0/1/2/3",
        "event_encoding": "1=Commit, 2=Policy False, 3=Policy True, 10+command=Hidden command",
        "commands": COMMANDS,
        "results": results,
        "scope": "Complete 16-state by 8-input tables for four generated pure kernels. No physical actuator, network failure or deployment was tested.",
    }


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "evidence/transition_table.csv"
    print(json.dumps(audit(source), ensure_ascii=False, indent=2))
