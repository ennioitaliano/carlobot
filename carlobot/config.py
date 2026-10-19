import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CATEGORIES_CACHE_DIR = DATA_DIR / "categories"
DATA_DIR.mkdir(exist_ok=True)
CATEGORIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)

PERSISTENCE_PATH = DATA_DIR / "persistence"
TOKEN_PATH = DATA_DIR / "token.json"

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TYPESAFE_API_KEY = os.environ["TYPESAFE_API_KEY"]
BUDGETING_2026_SPREADSHEET_ID = os.environ["BUDGETING_2026_SPREADSHEET_ID"]
EXPENSE_CATEGORIES_RANGE = os.environ["EXPENSE_CATEGORIES_RANGE"]
INCOME_CATEGORIES_RANGE = os.environ["INCOME_CATEGORIES_RANGE"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "google_service_account.json")
)
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
