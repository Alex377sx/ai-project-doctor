import tempfile
import unittest
from pathlib import Path

from project_doctor.__main__ import check_project


class DoctorTests(unittest.TestCase):
    def test_reports_missing_basics(self):
        with tempfile.TemporaryDirectory() as directory:
            report = check_project(Path(directory))
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("missing-readme", codes)
            self.assertIn("missing-license", codes)

    def test_detects_possible_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Demo", encoding="utf-8")
            key_name = "api_" + "key"
            (root / "config.py").write_text(f'{key_name} = "123456789abcdef"', encoding="utf-8")
            report = check_project(root)
            self.assertIn("possible-secret", {item["code"] for item in report["findings"]})


if __name__ == "__main__":
    unittest.main()
