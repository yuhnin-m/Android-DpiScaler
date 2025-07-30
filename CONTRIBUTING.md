# Contributing

## Development setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
pip install -e .
```

## Local checks
```bash
ruff check .
python -m pytest
```

## Branches and commits
- Branch from `main`.
- Keep PRs focused and small.
- Use clear commit messages.

## Pull requests
1. Describe what changed and why.
2. Include test notes.
3. Update docs when behavior changes.

## Code style
- Python: PEP 8
- Prefer small functions with clear responsibility.
- Avoid silent exception swallowing.
