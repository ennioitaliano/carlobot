import sys
from datetime import datetime

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

import environment
from categories.categories_builder import CategoriesBuilder
from transaction import Transaction
from transaction_type import TransactionType


class MessageParser:
    client = TypeSafeClient()
    _builder = CategoriesBuilder()
    exp_data = _builder.get_categories(TransactionType.EXPENSE)
    inc_data = _builder.get_categories(TransactionType.INCOME)

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
        type = TransactionType[answer.choice]

        if type == TransactionType.NONE:
            raise ValueError("Not a transaction")

        return (answer, type)

    def __category(self, message: str, type: TransactionType = TransactionType.EXPENSE):
        data = self.exp_data if type == TransactionType.EXPENSE else self.inc_data
        cat_criteria = {cat: info.get("description", "") for cat, info in data.items()}

        response = self.client.system_one(
            state=message,
            questions={
                "category": Choice(
                    instructions=f"To what category does this {type.name.lower()} transaction belong?",
                    criteria=cat_criteria,
                ),
            },
        )
        return response.answers["category"]

    def __subcategory(self, message: str, type: TransactionType, category: str):
        data = self.exp_data if type == TransactionType.EXPENSE else self.inc_data
        sub_criteria = data.get(category, {}).get("subcategories", {})

        response = self.client.system_one(
            state=message,
            questions={
                "subcategory": Choice(
                    instructions=f"To what subcategory of {category} does this {type.name.lower()} transaction belong?",
                    criteria=sub_criteria,
                ),
            },
        )
        return response.answers["subcategory"]

    def parse(self, message: str) -> Transaction:
        answer, type = self.__transaction_type(message)
        category_answer = self.__category(message, type)
        subcategory_answer = self.__subcategory(message, type, category_answer.choice)

        return Transaction(
            type=(answer, type),
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
