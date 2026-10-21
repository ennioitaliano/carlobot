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
        current_month = current_date.strftime("%b")

        range = (
            f"{current_month}!B3:F3"
            if transaction_type == TransactionType.EXPENSE
            else f"{current_month}!H3:K3"
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
