"""Shared helpers used by scripts and modules.

Centralizes the .env loader and the UTF-16/UTF-8 file decoding that were
previously duplicated across scripts/.
"""
from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path | str = ".env") -> None:
    """Minimal .env loader — sets os.environ without overriding existing vars."""
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def read_text_auto(path: Path | str) -> str:
    """Read a text file, auto-detecting UTF-16 BOM (PowerShell `>` redirection)."""
    raw = Path(path).read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8")
