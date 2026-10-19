from dataclasses import dataclass
from datetime import datetime
from textwrap import dedent
from typing import override

from typesafe_sdk import Answer

from carlobot.domain.types import TransactionType


@dataclass
class Transaction:
    transaction_type: tuple[Answer, TransactionType]
    date: datetime
    amount: float
    description: str
    category: Answer
    subcategory: Answer

    @override
    def __repr__(self) -> str:
        return dedent(f"""
        *Type*
            - *Choice*: {self.transaction_type[0].choice}
            - *Confidence*: {self.transaction_type[0].confidence}
            - *Enum*: {self.transaction_type[1]}

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
            *Category*: {self.category.choice.capitalize()}
            *Sub-category*: {self.subcategory.choice}
        """)
