import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.local")

DATA_DIR = BASE_DIR / "data"
CATEGORIES_CACHE_DIR = DATA_DIR / "categories"
DATA_DIR.mkdir(exist_ok=True)
CATEGORIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)

PERSISTENCE_PATH = DATA_DIR / "persistence"

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TYPESAFE_API_KEY = os.environ["TYPESAFE_API_KEY"]
GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
EXPENSE_CATEGORIES_RANGE = os.environ["EXPENSE_CATEGORIES_RANGE"]
INCOME_CATEGORIES_RANGE = os.environ["INCOME_CATEGORIES_RANGE"]
EXPENSE_INSERT_RANGE = os.environ["EXPENSE_INSERT_RANGE"]
INCOME_INSERT_RANGE = os.environ["INCOME_INSERT_RANGE"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]
GOOGLE_SERVICE_ACCOUNT_FILE = str(BASE_DIR / GOOGLE_SERVICE_ACCOUNT_FILE)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
