import tempfile
import unittest
from pathlib import Path

from project_doctor.__main__ import check_project, validate_repository_url


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


    def test_normalizes_github_repository_url(self):
        target = "https://github.com/example/project"
        self.assertEqual(validate_repository_url(target), "https://github.com/example/project.git")

    def test_rejects_non_repository_github_url(self):
        with self.assertRaises(ValueError):
            validate_repository_url("https://github.com/example/project/blob/main/README.md")


if __name__ == "__main__":
    unittest.main()
