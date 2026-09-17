# Contributing

Thanks for taking the time to improve AI Project Doctor.

## Before opening an issue

Please check whether the problem has already been reported. A useful bug report includes:

- The operating system and Python version
- The command that was run
- The relevant output
- A small reproduction project, when possible

Please remove passwords, API keys, and other private information before sharing logs or files.

## Pull requests

Keep changes focused and explain the user problem they solve. Add or update tests when behavior changes, and run:

```bash
python -m unittest discover -s tests -v
```

The project favors small checks with clear recommendations over a large framework. New checks should avoid false positives and should explain what the user can do next.
