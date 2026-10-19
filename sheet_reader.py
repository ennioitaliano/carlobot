from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import environment
from sheet_authenticator import SheetAuthenticator
from transaction_type import TransactionType


class SheetReader:
    authenticator = SheetAuthenticator()
    credentials = authenticator.authenticate()

    def get_categories_sheet(self, type: TransactionType):
        try:
            service = build("sheets", "v4", credentials=self.credentials)
            sheet = service.spreadsheets()

            result = (
                sheet.values()
                .get(
                    spreadsheetId=environment.BUDGETING_2026_SPREADSHEET_ID,
                    range=environment.EXPENSE_CATEGORIES_RANGE
                    if type == TransactionType.EXPENSE
                    else environment.INCOME_CATEGORIES_RANGE,
                    majorDimension="COLUMNS",
                )
                .execute()
            )
            values = result.get("values", [])

            if not values:
                raise LookupError(f"No values found for categories in range {range}")

            categories = {}
            for col in values:
                if col:
                    category_name = col[0]
                    subcategories = [s for s in col[1:] if s]
                    categories[category_name] = subcategories

            return categories
        except HttpError as err:
            print(err)
            return {}


if __name__ == "__main__":
    reader = SheetReader()

    expense_categories = reader.get_categories_sheet(TransactionType.EXPENSE)
    income_categories = reader.get_categories_sheet(TransactionType.INCOME)

    print(expense_categories)
    print("\n\n")
    print(income_categories)
