from __future__ import annotations

import sqlite3
from typing import Any

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_: Any = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    return get_db().execute(query, params).fetchall()


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return get_db().execute(query, params).fetchone()


def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    db = get_db()
    db.execute(query, params)
    db.commit()
