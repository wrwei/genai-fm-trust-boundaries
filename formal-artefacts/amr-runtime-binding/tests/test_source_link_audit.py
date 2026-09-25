"""A self-consistent logged output must not hide invented facts or commands."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import unittest
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
if importlib.util.find_spec('source_link_audit'):
    from source_link_audit import SourceLinkAudit
else:
    SourceLinkAudit = None


class SourceLinkTests(unittest.TestCase):
    def check_mutation(self, kind, mutate, *, only_proceed=False, recompute=False):
        self.assertIsNotNone(SourceLinkAudit, 'source-to-command independent auditor missing')
        from source_check import ROOT, language
        from binding import V2
        selected = json.loads((V2/'evidence/source/summary.json').read_bytes())['selected']
        program = language.parse_program((ROOT/selected['path']).read_text(encoding='utf-8'))
        out = BASE/'evidence/run-2026-09-22'
        checker = SourceLinkAudit(json.loads((out/'effective-parameters.json').read_bytes()), program)
        with gzip.open(out/'none.jsonl.gz', 'rt', encoding='utf-8') as stream:
            for line in stream:
                row = json.loads(line)
                if row['kind'] == kind:
                    if only_proceed and row['raw_action'] != 'Proceed':
                        checker.observe(row)
                        continue
                    mutate(row)
                    if recompute:
                        row['raw_action'], row['raw_next'] = language.eval_step(program, row['prior_mode'], row['facts'])
                    with self.assertRaises(AssertionError):
                        checker.observe(row)
                    return
                checker.observe(row)
        self.fail('fixture has no target event')

    def test_rejects_invented_input_fact(self):
        self.check_mutation('source_step', lambda r: r['facts'].update(TaskActive=False))

    def test_rejects_action_to_motion_mismatch(self):
        self.check_mutation('source_step', lambda r: r.update(physical_intent='Proceed'))

    def test_rejects_command_without_source_origin(self):
        self.check_mutation('command_issued', lambda r: r['command'].update(intent='Proceed'))

    def test_rejects_self_consistent_output_from_false_observation(self):
        self.check_mutation('source_step', lambda r: r['facts'].update(ObservationUsable=False),
                            only_proceed=True, recompute=True)


if __name__ == '__main__':
    unittest.main()
