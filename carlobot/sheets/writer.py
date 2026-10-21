from datetime import datetime
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from carlobot import config
from carlobot.domain.models import Transaction
from carlobot.domain.types import TransactionType
from carlobot.sheets.auth import SheetAuthenticator


class SheetWriter:
    def __init__(self) -> None:
        self.authenticator = SheetAuthenticator()
        self.credentials = self.authenticator.authenticate()

    def _get_range(self, transaction_type: TransactionType) -> str:
        local_timezone = ZoneInfo("Europe/Rome")
        current_date = datetime.now(tz=local_timezone).date()
        months = (
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        )
        current_month = months[current_date.month - 1]

        range = (
            current_month + config.EXPENSE_INSERT_RANGE
            if transaction_type == TransactionType.EXPENSE
            else current_month + config.INCOME_INSERT_RANGE
        )

        return range

    def write_values(self, transaction: Transaction):
        service = build("sheets", "v4", credentials=self.credentials)
        sheet = service.spreadsheets()
        target_range = self._get_range(transaction.transaction_type[1])

        sheet.values().append(
            spreadsheetId=config.BUDGETING_2026_SPREADSHEET_ID,
            range=target_range,
            valueInputOption="USER_ENTERED",
            body={"values": [transaction.list_values()]},
        ).execute()
