from __future__ import annotations

from typing import Generator
from database.session import get_session


def get_db() -> Generator:
    db = get_session()
    try:
        yield db
    finally:
        db.close()
