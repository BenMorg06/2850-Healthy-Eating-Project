from __future__ import annotations

from sqlite3 import Row
from typing import Any
from uuid import uuid4

from flask import request, session
from werkzeug.security import generate_password_hash

from .constants import CLIENTS, FOODS
from .db import execute, fetch_all, fetch_one, get_db
from .helpers import today_str


def init_db() -> None:
    db = get_db()
    cur = db.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            gender TEXT,
            weight REAL,
            status TEXT DEFAULT 'User',
            is_professional INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS foods (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            img TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS favourites (
            user_id TEXT NOT NULL,
            food_id TEXT NOT NULL,
            PRIMARY KEY (user_id, food_id)
        );

        CREATE TABLE IF NOT EXISTS diary_records (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            food_id TEXT,
            name TEXT NOT NULL,
            grams REAL NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            category TEXT NOT NULL,
            img TEXT,
            ingredients TEXT
        );

        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
            date TEXT NOT NULL,
            read_by_client INTEGER DEFAULT 0
        );
        """
    )

    for food in FOODS:
        cur.execute(
            """
            INSERT OR IGNORE INTO foods (id, name, category, img, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                food['id'], food['name'], food['category'], food['img'],
                food['calories'], food['protein'], food['carbs'], food['fat'],
            ),
        )

    default_password = generate_password_hash('123456')
    for user_id, username, email, status in CLIENTS:
        cur.execute(
            """
            INSERT OR IGNORE INTO users (id, email, username, password_hash, gender, status, is_professional)
            VALUES (?, ?, ?, ?, 'Prefer not to say', ?, 0)
            """,
            (user_id, email, username, default_password, status),
        )

    cur.execute(
        """
        INSERT OR IGNORE INTO users (id, email, username, password_hash, gender, status, is_professional)
        VALUES ('pro-1', 'professional@example.com', 'Professional', ?, 'Prefer not to say', 'Dietitian', 1)
        """,
        (default_password,),
    )

    cur.execute("INSERT OR IGNORE INTO favourites (user_id, food_id) VALUES ('client-1', 'food-3')")
    cur.execute("INSERT OR IGNORE INTO favourites (user_id, food_id) VALUES ('client-1', 'food-5')")

    seed_records = [
        (str(uuid4()), 'client-1', today_str(), 'database', 'food-3', 'Chicken Breast', 150, 248, 46.5, 0, 5.4, 'Protein', 'https://picsum.photos/seed/f3/300/200', None),
        (str(uuid4()), 'client-2', today_str(), 'database', 'food-1', 'Fresh Salad', 220, 187, 4.6, 18.7, 7, 'Vegetable', 'https://picsum.photos/seed/f1/300/200', None),
        (str(uuid4()), 'client-3', today_str(), 'database', 'food-5', 'Avocado Toast', 140, 254.8, 7.6, 26.9, 11.3, 'Breakfast', 'https://picsum.photos/seed/f5/300/200', None),
    ]
    for row in seed_records:
        cur.execute(
            """
            INSERT OR IGNORE INTO diary_records
            (id, client_id, date, type, food_id, name, grams, calories, protein, carbs, fat, category, img, ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )

    cur.execute(
        """
        INSERT OR IGNORE INTO notes (id, client_id, author, message, date, read_by_client)
        VALUES ('seed-note-1', 'client-1', 'Professional',
        'Please keep dinner lighter today and reduce oily sauces.', ?, 0)
        """,
        (today_str(),),
    )

    db.commit()


def current_user() -> Row | None:
    user_id = session.get('user_id')
    if not user_id:
        return None
    return fetch_one('SELECT * FROM users WHERE id = ?', (user_id,))


def get_foods() -> list[Row]:
    return fetch_all('SELECT * FROM foods ORDER BY id')


def get_food(food_id: str) -> Row | None:
    return fetch_one('SELECT * FROM foods WHERE id = ?', (food_id,))


def find_food_by_name(name: str) -> Row | None:
    return fetch_one('SELECT * FROM foods WHERE lower(name) = lower(?)', (name.strip(),))


def get_favourite_ids(user_id: str) -> set[str]:
    return {row['food_id'] for row in fetch_all('SELECT food_id FROM favourites WHERE user_id = ?', (user_id,))}


def get_records(client_id: str, selected_date: str) -> list[Row]:
    return fetch_all(
        'SELECT * FROM diary_records WHERE client_id = ? AND date = ? ORDER BY rowid DESC',
        (client_id, selected_date),
    )


def sum_totals(records: list[Row]) -> dict[str, float]:
    totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}
    for row in records:
        totals['calories'] += float(row['calories'])
        totals['protein'] += float(row['protein'])
        totals['carbs'] += float(row['carbs'])
        totals['fat'] += float(row['fat'])
    return {key: round(value, 1) for key, value in totals.items()}


def build_context(page: str | None = None) -> dict[str, Any]:
    user = current_user()
    today = today_str()
    page = page or request.args.get('page', 'dashboard')
    diary_date = request.args.get('diary_date', today)
    professional_date = request.args.get('professional_date', today)
    selected_client_id = request.args.get('client_id', user['id'] if user else 'client-1')

    foods = get_foods()
    favourite_ids = get_favourite_ids(user['id']) if user else set()
    favourite_foods = [food for food in foods if food['id'] in favourite_ids]

    diary_records = get_records(user['id'], diary_date) if user else []
    diary_totals = sum_totals(diary_records)

    clients = fetch_all('SELECT id, username, status FROM users WHERE is_professional = 0 ORDER BY username')
    professional_records = get_records(selected_client_id, professional_date)
    professional_totals = sum_totals(professional_records)
    selected_client = fetch_one('SELECT id, username, status FROM users WHERE id = ?', (selected_client_id,))

    user_notes = fetch_all('SELECT * FROM notes WHERE client_id = ? ORDER BY rowid DESC', (user['id'],)) if user else []
    unread_user_notes = sum(1 for note in user_notes if not note['read_by_client'])
    pro_notes = fetch_all('SELECT * FROM notes WHERE client_id = ? ORDER BY rowid DESC', (selected_client_id,))

    return {
        'page': page,
        'today': today,
        'user': user,
        'foods': foods,
        'favourite_ids': favourite_ids,
        'favourite_foods': favourite_foods,
        'diary_date': diary_date,
        'diary_records': diary_records,
        'diary_totals': diary_totals,
        'clients': clients,
        'selected_client_id': selected_client_id,
        'selected_client': selected_client,
        'professional_date': professional_date,
        'professional_records': professional_records,
        'professional_totals': professional_totals,
        'user_notes': user_notes,
        'unread_user_notes': unread_user_notes,
        'pro_notes': pro_notes,
        'quick_add_food_id': request.args.get('quick_add_food_id', ''),
        'food_lookup_result': request.args.get('food_lookup_result', ''),
        'entry_mode': request.args.get('entry_mode', 'lookup'),
    }
