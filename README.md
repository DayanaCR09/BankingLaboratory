# Banking Laboratory

A small Python banking application for managing customers and accounts. The
interactive CLI supports account creation, deposits, withdrawals, currency
conversion, and transfers.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup

From the repository root, install the exact dependencies recorded in
`uv.lock`:

```powershell
uv sync --locked
```

The `--locked` option ensures the lockfile is current and does not silently
change dependency versions.

## Run the application

```powershell
uv run python main.py
```

Use the numbered menu to add adult customers, create accounts, perform
transactions, or exit. Account numbers must contain exactly 10 digits.

## Run the CI pipeline locally

The same checks run for pull requests opened, updated, or reopened. Run them
from the repository root:

```powershell
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run python -m pytest
```

The test suite verifies account operations, customer validation, and transfers.
`python -m pytest` runs pytest through the project interpreter and keeps the
repository root importable for the `src` package.
