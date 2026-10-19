import os

from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TYPESAFE_API_KEY = os.environ["TYPESAFE_API_KEY"]
BUDGETING_2026_SPREADSHEET_ID = os.environ["BUDGETING_2026_SPREADSHEET_ID"]
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
EXPENSE_CATEGORIES_RANGE = os.environ["EXPENSE_CATEGORIES_RANGE"]
INCOME_CATEGORIES_RANGE = os.environ["INCOME_CATEGORIES_RANGE"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", "google_service_account.json"
)
