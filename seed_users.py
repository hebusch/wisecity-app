"""Idempotent seed script — inserts default local users if they don't exist.

Called automatically from the FastAPI lifespan at startup.
Uses ON CONFLICT DO NOTHING so re-running is safe.
"""

import bcrypt
from api import database

_USERS = [
    ("heinzbuschcarvajal@gmail.com", "Treinz12.."),
    ("constanzatoledo1996@gmail.com", "ctoledo2026"),
]

for _email, _password in _USERS:
    _hashed = bcrypt.hashpw(_password.encode(), bcrypt.gensalt()).decode()
    database.create_local_user(_email, _hashed)
