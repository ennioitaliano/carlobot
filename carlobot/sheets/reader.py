from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from carlobot import config
from carlobot.domain.types import TransactionType
from carlobot.sheets.auth import SheetAuthenticator


class SheetReader:
    def __init__(self) -> None:
        self.authenticator = SheetAuthenticator()
        self.credentials = self.authenticator.authenticate()

    def get_categories_sheet(self, type: TransactionType):
        target_range = (
            config.EXPENSE_CATEGORIES_RANGE
            if type == TransactionType.EXPENSE
            else config.INCOME_CATEGORIES_RANGE
        )

        service = build("sheets", "v4", credentials=self.credentials)
        sheet = service.spreadsheets()

        result = (
            sheet.values()
            .get(
                spreadsheetId=config.BUDGETING_2026_SPREADSHEET_ID,
                range=target_range,
                majorDimension="COLUMNS",
            )
            .execute()
        )
        values = result.get("values", [])

        if not values:
            raise LookupError(f"No values found for categories in range {target_range}")

        categories = {}
        for col in values:
            if col:
                category_name = col[0]
                subcategories = [s for s in col[1:] if s]
                categories[category_name] = subcategories

        return categories
