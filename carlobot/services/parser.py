import sys
from datetime import datetime

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

from carlobot import config
from carlobot.categories.builder import CategoriesBuilder
from carlobot.domain import Transaction, TransactionType


class MessageParser:
    def __init__(
        self, exp_data: dict | None = None, inc_data: dict | None = None
    ) -> None:
        self.client = TypeSafeClient()

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

    def __transaction_type(self, message: str):
        response = self.client.system_one(
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

    def __category(self, message: str, transaction_type: TransactionType = TransactionType.EXPENSE):
        data = self.exp_data if transaction_type == TransactionType.EXPENSE else self.inc_data
        cat_criteria = {cat: info.get("description", "") for cat, info in data.items()}

        response = self.client.system_one(
            state=message,
            questions={
                "category": Choice(
                    instructions=f"To what category does this {transaction_type.name.lower()} transaction belong?",
                    criteria=cat_criteria,
                ),
            },
        )
        return response.answers["category"]

    def __subcategory(self, message: str, transaction_type: TransactionType, category: str):
        data = self.exp_data if transaction_type == TransactionType.EXPENSE else self.inc_data
        sub_criteria = data.get(category, {}).get("subcategories", {})

        response = self.client.system_one(
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
        answer, transaction_type = self.__transaction_type(message)
        category_answer = self.__category(message, transaction_type)
        subcategory_answer = self.__subcategory(message, transaction_type, category_answer.choice)

        return Transaction(
            transaction_type=(answer, transaction_type),
            date=datetime.now(),
            amount=0.0,
            description="",
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
