from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / 'instance'
DB_PATH = INSTANCE_DIR / 'app.db'


class Config:
    SECRET_KEY = 'dev-secret-key-change-me'
    DATABASE = DB_PATH
