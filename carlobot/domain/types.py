from enum import Enum


class TransactionType(Enum):
    EXPENSE = "money spent"
    INCOME = "money earned"
    NONE = "not a monetary transaction at all"
