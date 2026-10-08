import sys
from enum import Enum

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

import environment


class TransactionType(Enum):
    EXPENSE = "money spent"
    INCOME = "money earned"
    NONE = "not a monetary transaction at all"


class MessageParser:
    client = TypeSafeClient()

    def transaction_type(self, message: str):
        response = self.client.system_one(
            state=message,
            questions={
                "type": Choice(
                    instructions="What kind of transaction is this",
                    criteria={type.name: type.value for type in TransactionType},
                ),
            },
        )

        answer = response.answers["type"]

        return (answer, TransactionType[answer.choice])


if __name__ == "__main__":
    message_parser = MessageParser()
    answer, type = message_parser.transaction_type(sys.argv[1])
    print(f"Choice: {answer.choice}\nConfidence: {answer.confidence}\nType: {type}")
