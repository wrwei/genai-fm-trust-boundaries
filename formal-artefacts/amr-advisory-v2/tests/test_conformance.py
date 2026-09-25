"""Cross-tool table corruption must fail; Python is not its own expected oracle."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('conformance'):
    import conformance as c
else:
    c=None


class ConformanceTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(c,'cross-tool conformance not implemented')

    def test_full_hol_table_and_truncated_or_corrupt_table(self):
        lines=c.CORE_CSV.read_text().splitlines()
        good=c.check_core(lines)
        self.assertEqual(good['rows'],11664)
        self.assertEqual(good['mismatches'],[])
        changed=lines[:]
        fields=changed[0].split(',')
        fields[7]='0' if fields[7]=='1' else '1'
        changed[0]=','.join(fields)
        self.assertGreater(len(c.check_core(changed)['mismatches']),0)
        with self.assertRaises(ValueError): c.check_core(lines[:-1])


if __name__=='__main__': unittest.main()
