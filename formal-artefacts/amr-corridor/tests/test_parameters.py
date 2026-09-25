"""Parameter identity must not silently disagree with the fixed physical model."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation import parameters, PARAMETER_PATH


class ParameterTests(unittest.TestCase):
    def test_changed_robot_width_is_rejected_instead_of_ignored(self):
        changed = json.loads(PARAMETER_PATH.read_text(encoding='utf-8'))
        changed['robot']['width'] = 1.8
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'parameters.json'
            path.write_text(json.dumps(changed), encoding='utf-8')
            with self.assertRaises(ValueError):
                parameters(path)


if __name__ == '__main__':
    unittest.main()
