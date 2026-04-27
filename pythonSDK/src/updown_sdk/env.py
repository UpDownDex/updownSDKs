from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_sdk_dotenv(*, override: bool = False) -> Optional[Path]:
    """
    Load .env for pythonSDK scripts.

    Priority:
    - pythonSDK/.env
    - tsSDK/.env (repo root)
    """
    here = Path(__file__).resolve()
    python_sdk_root = here.parents[2]  # pythonSDK/
    ts_sdk_root = python_sdk_root.parent  # tsSDK/

    candidates = [
        python_sdk_root / ".env",
        ts_sdk_root / ".env",
    ]

    for p in candidates:
        if p.exists():
            load_dotenv(dotenv_path=str(p), override=override)
            return p

    # nothing loaded
    return None

