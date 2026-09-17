import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
]
IGNORED = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea"}


def files_in(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not any(part in IGNORED for part in path.parts):
            yield path


def check_project(root: Path, display_root: Optional[str] = None) -> dict:
    files = list(files_in(root))
    names = {path.name.lower() for path in files}
    findings = []

    def add(severity, code, message, path=None):
        finding = {"severity": severity, "code": code, "message": message}
        if path:
            finding["path"] = str(path.relative_to(root))
        findings.append(finding)

    if not any(name.startswith("readme") for name in names):
        add("high", "missing-readme", "Add a README explaining installation and usage.")
    if not any(name in {"license", "license.md", "license.txt"} for name in names):
        add("medium", "missing-license", "Add an explicit open-source license.")
    if not any(part.lower() in {"test", "tests", "spec", "specs"} for path in files for part in path.parts):
        add("medium", "missing-tests", "Add an automated test directory or test suite.")

    manifests = {"package.json", "pyproject.toml", "requirements.txt", "cargo.toml", "go.mod"}
    detected = sorted(name for name in names if name in manifests)
    if not detected:
        add("low", "no-metadata", "No common package metadata file was detected.")

    lockfiles = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock", "cargo.lock"}
    if detected and not names.intersection(lockfiles):
        add("low", "missing-lockfile", "Consider committing a dependency lockfile for reproducible installs.")

    for path in files:
        try:
            if path.stat().st_size > 5 * 1024 * 1024:
                add("medium", "large-file", "File is larger than 5 MiB; consider Git LFS or generated output.", path)
            if path.stat().st_size <= 512 * 1024 and path.suffix.lower() in {".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".env"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                    add("critical", "possible-secret", "Possible credential detected; rotate it and remove it from history.", path)
        except OSError:
            add("low", "unreadable-file", "Could not read this file.", path)

    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        add("low", "not-git-repository", "Run this inside a Git repository for complete checks.")

    weights = {"critical": 25, "high": 15, "medium": 8, "low": 3}
    score = max(0, 100 - sum(weights[item["severity"]] for item in findings))
    return {"version": "0.1.0", "root": display_root or str(root), "score": score, "findings": findings}

\n\ndef validate_repository_url(target: str) -> str:
    parsed = urlparse(target)
    if parsed.scheme.lower() != "https" or parsed.netloc.lower() != "github.com":
        raise ValueError("Only HTTPS GitHub repository URLs are supported.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("Use a repository URL such as https://github.com/owner/repository.")

    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository or parsed.query or parsed.fragment:
        raise ValueError("Use the repository URL without query parameters or a file path.")

    return f"https://github.com/{owner}/{repository}.git"


def inspect_target(target: str) -> dict:
    if not target.lower().startswith("https://"):
        return check_project(Path(target).resolve())

    repository_url = validate_repository_url(target)
    with tempfile.TemporaryDirectory(prefix="project-doctor-") as temporary_directory:
        checkout_path = Path(temporary_directory) / "repository"
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", "--", repository_url, str(checkout_path)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError as error:
            raise RuntimeError("Git is required to analyze a GitHub URL.") from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("The repository clone timed out after 120 seconds.") from error
        except subprocess.CalledProcessError as error:
            detail = error.stderr.strip() or "Git could not clone the repository."
            raise RuntimeError(detail) from error

        return check_project(checkout_path, display_root=target)


def main():
    parser = argparse.ArgumentParser(description="Create a local health report for a software repository.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()
    try:
        report = inspect_target(args.path)
    except (RuntimeError, ValueError) as error:
        parser.error(str(error))
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"AI Project Doctor | score: {report['score']}/100")
    for item in report["findings"]:
        location = f" [{item['path']}]" if "path" in item else ""
        print(f"- {item['severity'].upper()}: {item['message']}{location}")


if __name__ == "__main__":
    main()
