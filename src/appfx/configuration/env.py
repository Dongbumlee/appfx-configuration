"""Environment variable loading helpers."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


def load_environment_variables(
    env_file: str | Path = ".env",
    *,
    override: bool = False,
) -> dict[str, str]:
    """Load variables from a .env file into ``os.environ``.

    Returns the keys declared by the .env file with the effective values now in
    the process environment. Existing process environment values win by default.
    """
    env_path = Path(env_file)
    if not env_path.exists():
        return {}

    dotenv_entries = {
        key: value
        for key, value in dotenv_values(env_path).items()
        if value is not None
    }
    load_dotenv(env_path, override=override)

    return {
        key: value
        for key in dotenv_entries
        if (value := os.environ.get(key)) is not None
    }
