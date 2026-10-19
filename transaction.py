from datetime import datetime
from textwrap import dedent
from typing import override

from typesafe_sdk import Answer

from transaction_type import TransactionType


class Transaction:
    type: tuple[Answer, TransactionType]
    date: datetime
    amount: float
    description: str
    category: Answer
    subcategory: Answer

    def __init__(
        self,
        type: tuple[Answer, TransactionType],
        date: datetime,
        amount: float,
        description: str,
        category: Answer,
        subcategory: Answer,
    ):
        self.type = type
        self.date = date
        self.amount = amount
        self.description = description
        self.category = category
        self.subcategory = subcategory

    @override
    def __repr__(self) -> str:
        return dedent(f"""
        *Type*
            - *Choice*: {self.type[0].choice}
            - *Confidence*: {self.type[0].confidence}
            - *Enum*: {self.type[1]}

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
            *Type*: {self.type[1].name.capitalize()}
            *Category*: {self.category.choice.capitalize()}
            *Sub-category*: {self.subcategory.choice}
        """)
