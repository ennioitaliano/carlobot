import asyncio
import base64
import re
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

from google import genai
from pydantic import BaseModel, Field
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, NoulCriteria, Score

from carlobot import config
from carlobot.categories.builder import CategoriesBuilder
from carlobot.domain import Transaction, TransactionType


class MessageParser:
    def __init__(
        self, exp_data: dict | None = None, inc_data: dict | None = None
    ) -> None:
        self.ts_client = AsyncTypeSafeClient()
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

    async def _transaction_type(self, message: str):
        response = await self.ts_client.system_one(
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

    async def _date_confidence(self, message: str) -> float:
        response = await self.ts_client.system_one(
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

    async def _extract_date(self, message: str, current_date: date) -> date:
        interaction = await self.gemini_client.aio.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested date in YYYY-MM-DD, no formatting",
            input=f"""
                    The following message contains a date/timing info: '{message}'
                    What date can be extracted? Today is {current_date.strftime("%A, %F")}
                """,
        )

        return datetime.fromisoformat(interaction.output_text.strip()).date()

    async def _date(self, message: str) -> tuple[float, date]:
        confidence = await self._date_confidence(message)
        local_timezone = ZoneInfo("Europe/Rome")
        current_date = datetime.now(tz=local_timezone).date()

        if confidence < 0.5:
            return (confidence, current_date)

        output_date = await self._extract_date(message, current_date)

        if (output_date.month, output_date.year) != (
            current_date.month,
            current_date.year,
        ):
            raise ValueError("The bot can only log current-month transactions.")

        return (
            confidence,
            output_date,
        )

    async def _amount_description(
        self, message: str, transaction_type: TransactionType
    ) -> tuple[float, str]:
        if re.search("[a-zA-Z]", message) is None:
            raise ValueError("Missing description")

        class TransactionProperties(BaseModel):
            amount: float = Field(description="Amount of money of the transaction")
            description: str = Field(
                description=f"Description of the object of the {transaction_type.name.lower()} transaction, in Italian, maximum 3 words, no articles/prepositions, no reference to the transaction type (e.g., 'purchase', etc.)"
            )

        prompt = f"""
        The following message contains informations about an {transaction_type.name.lower()} transaction: '{message}'
        What is the amount of money involved and the object of the transaction?
        """

        interaction = await self.gemini_client.aio.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": TransactionProperties.model_json_schema(),
            },
        )

        transaction_props = TransactionProperties.model_validate_json(
            interaction.output_text
        )

        if transaction_props.amount == 0.0:
            raise ValueError("Missing amount")

        return (transaction_props.amount, transaction_props.description)

    async def _category(
        self, message: str, transaction_type: TransactionType = TransactionType.EXPENSE
    ):
        data = (
            self.exp_data
            if transaction_type == TransactionType.EXPENSE
            else self.inc_data
        )
        cat_criteria = {cat: info.get("description", "") for cat, info in data.items()}

        response = await self.ts_client.system_one(
            state=message,
            questions={
                "category": Choice(
                    instructions=f"To what category does this {transaction_type.name.lower()} transaction belong?",
                    criteria=cat_criteria,
                ),
            },
        )
        return response.answers["category"]

    async def _subcategory(
        self, message: str, transaction_type: TransactionType, category: str
    ):
        data = (
            self.exp_data
            if transaction_type == TransactionType.EXPENSE
            else self.inc_data
        )
        sub_criteria = data.get(category, {}).get("subcategories", {})

        response = await self.ts_client.system_one(
            state=message,
            questions={
                "subcategory": Choice(
                    instructions=f"To what subcategory of {category} does this {transaction_type.name.lower()} transaction belong?",
                    criteria=sub_criteria,
                ),
            },
        )
        return response.answers["subcategory"]

    async def _get_transcription(self, voice_message: bytearray, mime_type: str) -> str:
        audio_data = base64.b64encode(voice_message).decode("ascii")

        interaction = await self.gemini_client.aio.interactions.create(
            model="gemini-3.5-transcribe",
            input=[
                {
                    "type": "audio",
                    "data": audio_data,
                    "mime_type": mime_type,
                }
            ],
        )

        return interaction.output_text

    async def parse(
        self, message: str | bytearray, mime_type: str | None = None
    ) -> Transaction:
        if isinstance(message, bytearray):
            if mime_type is None:
                raise ValueError("Problem with voice message")

            message = await self._get_transcription(message, mime_type)

        type_answer, transaction_type = await self._transaction_type(message)
        date_confidence, date = await self._date(message)
        amount, description = await self._amount_description(message, transaction_type)
        category_answer = await self._category(message, transaction_type)
        subcategory_answer = await self._subcategory(
            message, transaction_type, category_answer.choice
        )

        return Transaction(
            transaction_type=(type_answer, transaction_type),
            date=(date_confidence, date),
            amount=amount,
            description=description,
            category=category_answer,
            subcategory=subcategory_answer,
        )


async def main() -> None:
    message_parser = MessageParser()

    async with message_parser.ts_client, message_parser.gemini_client.aio:
        try:
            transaction = await message_parser.parse(sys.argv[1])
            print(repr(transaction))
        except ValueError as e:
            print(f"⚠️ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
