"""Symmetric encryption for WiseCity credentials stored in DuckDB."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet


def _key_path() -> Path:
    db = Path(os.environ.get("DB_PATH", "gps.duckdb")).resolve()
    return db.parent / ".secret_key"


@lru_cache(maxsize=1)
def _load_key() -> bytes:
    path = _key_path()
    if path.exists():
        return path.read_bytes().strip()
    key = Fernet.generate_key()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)
    return key


def encrypt(plaintext: str) -> str:
    return Fernet(_load_key()).encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return Fernet(_load_key()).decrypt(ciphertext.encode()).decode()
