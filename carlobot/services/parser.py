import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

from google import genai
from typesafe_sdk import Choice, Noul, NoulCriteria, Score, TypeSafeClient

from carlobot import config
from carlobot.categories.builder import CategoriesBuilder
from carlobot.domain import Transaction, TransactionType


class MessageParser:
    def __init__(
        self, exp_data: dict | None = None, inc_data: dict | None = None
    ) -> None:
        self.ts_client = TypeSafeClient()
        self.gemini_client = genai.Client()

        if exp_data is None or inc_data is None:
            builder = CategoriesBuilder()

        self.exp_data = (
            exp_data
            if exp_data is not None
            else builder.get_categories(TransactionType.EXPENSE)
        )
        self.inc_data = (
            inc_data
            if inc_data is not None
            else builder.get_categories(TransactionType.INCOME)
        )

    def _transaction_type(self, message: str):
        response = self.ts_client.system_one(
            state=message,
            questions={
                "type": Choice(
                    instructions="What kind of transaction is this?",
                    criteria={type.name: type.value for type in TransactionType},
                ),
            },
        )

        answer = response.answers["type"]
        transaction_type = TransactionType[answer.choice]

        if transaction_type == TransactionType.NONE:
            raise ValueError("Not a transaction")

        return (answer, transaction_type)

    def _date_confidence(self, message: str) -> float:
        response = self.ts_client.system_one(
            state=message,
            questions={
                "type": Noul(
                    instructions="Does this message contains a date or timing information?",
                    criteria=NoulCriteria(
                        true="Mentions an absolute or relative date, like '2026-10-19', 'on Monday', 'two days ago', 'yesterday', etc.",
                        false="No sign of any timing indication",
                    ),
                ),
            },
        )

        return response.answers["type"].noul

    def _extract_date(self, message: str, current_date: date) -> date:
        interaction = self.gemini_client.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested date in YYYY-MM-DD, no formatting",
            input=f"""
                    The following message contains a date/timing info: '{message}'
                    What date can be extracted? Today is {current_date.strftime("%A, %F")}
                """,
        )

        return datetime.fromisoformat(interaction.output_text.strip()).date()

    def _date(self, message: str) -> tuple[float, date]:
        confidence = self._date_confidence(message)
        local_timezone = ZoneInfo("Europe/Rome")
        current_date = datetime.now(tz=local_timezone).date()

        if confidence < 0.5:
            return (answer.noul, current_date)

        output_date = self._extract_date(message, current_date)

        if output_date.month != current_date.month:
            raise ValueError("The bot can only log current-month transactions.")

        return (
            confidence,
            output_date,
        )

    def _description(self, message: str) -> str:
        interaction = self.gemini_client.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested description, in Italian, maximum 3 words, no articles/prepositions, no formatting",
            input=f"""
                    The following message contains informations about a transaction: '{message}'
                    What is the object of the transaction?
                """,
        )
        return interaction.output_text.lower()

    def _amount(self, message: str) -> float:
        interaction = self.gemini_client.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested float amount, no formatting",
            input=f"""
                    The following message contains informations about a transaction: '{message}'
                    What is the amount of money of the transaction?
                """,
        )
        return float(interaction.output_text)

    def _category(
        self, message: str, transaction_type: TransactionType = TransactionType.EXPENSE
    ):
        data = (
            self.exp_data
            if transaction_type == TransactionType.EXPENSE
            else self.inc_data
        )
        cat_criteria = {cat: info.get("description", "") for cat, info in data.items()}

        response = self.ts_client.system_one(
            state=message,
            questions={
                "category": Choice(
                    instructions=f"To what category does this {transaction_type.name.lower()} transaction belong?",
                    criteria=cat_criteria,
                ),
            },
        )
        return response.answers["category"]

    def _subcategory(
        self, message: str, transaction_type: TransactionType, category: str
    ):
        data = (
            self.exp_data
            if transaction_type == TransactionType.EXPENSE
            else self.inc_data
        )
        sub_criteria = data.get(category, {}).get("subcategories", {})

        response = self.ts_client.system_one(
            state=message,
            questions={
                "subcategory": Choice(
                    instructions=f"To what subcategory of {category} does this {transaction_type.name.lower()} transaction belong?",
                    criteria=sub_criteria,
                ),
            },
        )
        return response.answers["subcategory"]

    def parse(self, message: str) -> Transaction:
        type_answer, transaction_type = self._transaction_type(message)
        date_conf, date = self._date(message)
        amount = self._amount(message)
        description = self._description(message)
        category_answer = self._category(message, transaction_type)
        subcategory_answer = self._subcategory(
            message, transaction_type, category_answer.choice
        )

        return Transaction(
            transaction_type=(type_answer, transaction_type),
            date=(date_conf, date),
            amount=amount,
            description=description,
            category=category_answer,
            subcategory=subcategory_answer,
        )


if __name__ == "__main__":
    message_parser = MessageParser()
    try:
        transaction = message_parser.parse(sys.argv[1])
        print(repr(transaction))
        print(str(transaction))
    except ValueError as e:
        print(f"⚠️ Error: {e}")
