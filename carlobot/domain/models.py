from dataclasses import dataclass
from datetime import date
from textwrap import dedent
from typing import override

from typesafe_sdk import Answer

from carlobot.domain.types import TransactionType


@dataclass
class Transaction:
    transaction_type: tuple[Answer, TransactionType]
    date: tuple[float, date]
    amount: float
    description: str
    category: Answer
    subcategory: Answer

    def list_values(self) -> list[str]:
        if self.transaction_type[1] == TransactionType.EXPENSE:
            return [
                self.date[1].strftime("%F"),
                f"{self.amount}",
                self.description.lower(),
                self.category.choice,
                self.subcategory.choice,
            ]
        else:
            return [
                self.date[1].strftime("%F"),
                f"{self.amount}",
                self.description.lower(),
                self.subcategory.choice,
            ]

    @override
    def __repr__(self) -> str:
        return dedent(f"""
        *Type*
            - *Choice*: {self.transaction_type[0].choice}
            - *Confidence*: {self.transaction_type[0].confidence}
            - *Enum*: {self.transaction_type[1]}

        *Date*
            - *Confidence:* {self.date[0]}
            - *Date:* {self.date[1].strftime("%F")}

        *Amount:* {self.amount}

        *Description:* {self.description}

        *Category*
            - *Choice*: {self.category.choice}
            - *Confidence*: {self.category.confidence}

        *Sub-category*
            - *Choice*: {self.subcategory.choice}
            - *Confidence*: {self.subcategory.confidence}
            """)

    @override
    def __str__(self) -> str:
        return dedent(f"""
            *Type*: {self.transaction_type[1].name.capitalize()}
            *Date:* {self.date[1].strftime("%F")}
            *Amount:* {self.amount}€
            *Description:* {self.description.capitalize()}
            *Category*: {self.category.choice.capitalize()}
            *Sub-category*: {self.subcategory.choice}
        """)
