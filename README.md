# AI Project Doctor

> A small, local checkup for software projects.

Most repositories do not fail because of one dramatic bug. They become difficult to maintain through a collection of small problems: missing documentation, no tests, an untracked lockfile, oversized files, or a credential accidentally left in source code.

AI Project Doctor gives you a quick health report before those problems become somebody else's surprise. Point it at a project and it checks the things that are easy to forget when you are focused on building features.

The first version is deliberately simple. It runs locally, reads the files it needs, and does not upload your source code or require an API key.

This is my first public open-source project. I am keeping the first release small so the checks are easy to understand, easy to test, and useful to other developers.

## What it checks

The current checks cover:

- A usable README and an explicit license
- A test directory or test suite
- Common package metadata such as `package.json` or `pyproject.toml`
- Dependency lockfiles for reproducible installs
- Files larger than 5 MiB
- Common patterns that may indicate an exposed secret
- Whether the target directory is a Git repository

The score is only a starting point. The useful part is the list of findings and the suggested next action.

## Try it

From the repository root:

```bash
python -m project_doctor .
```

To save a machine-readable report:

```bash
python -m project_doctor . --json report.json
```

Example output:

```text
AI Project Doctor | score: 73/100
- MEDIUM: Add an automated test directory or test suite.
- LOW: Consider committing a dependency lockfile for reproducible installs.
```

No installation step is required for the current development version. Python 3.9 or newer is recommended.

## Why this exists

There are excellent tools for deep security analysis and dependency scanning. This project focuses on the short checkup that happens before those tools: the five-minute review that tells you whether a repository is understandable, reproducible, and safe enough to share.

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

The project intentionally has no mandatory third-party dependencies. That keeps the first run predictable and makes the tool usable in a fresh environment or CI job.

## Roadmap

Planned improvements are ordered around useful reports rather than a large framework:

- GitHub Actions and CI configuration checks
- Dependency vulnerability adapters
- HTML reports and score history
- Optional AI explanations that users explicitly enable
- Plugin checks for Python, Node.js, Rust, Go, and Roblox/Luau projects
- A GitHub Action for checking every pull request

Suggestions and small pull requests are welcome. If a check is noisy or gives a recommendation without enough context, that is a bug worth reporting.

## License

MIT

## Project

[View AI Project Doctor on GitHub](https://github.com/Alex377sx/ai-project-doctor)
