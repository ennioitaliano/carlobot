import asyncio
import json
from pathlib import Path

from google import genai

from carlobot import config
from carlobot.domain.types import TransactionType
from carlobot.sheets.reader import SheetReader


class CategoriesBuilder:
    def __init__(self) -> None:
        self._gemini_client = genai.Client()

    async def _generate_cat_descr(
        self, cat_name: str, subcats: list[str], transaction_type: TransactionType
    ) -> str:
        interaction = await self._gemini_client.aio.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested description, no formatting, max 140 chars",
            input=f"""
                    I have a spreadsheet to manage my finances, tracking income and expenses.
                    Write a description for the '{cat_name}' {transaction_type.name.lower()} category, serving exclusively as a criteria to understand whether a certain transaction belongs to it.
                    Keep into consideration also its subcategories: {", ".join(subcats)}
                """,
        )
        return interaction.output_text

    async def _generate_sub_descr(
        self, sub_name: str, cat_name: str, transaction_type: TransactionType
    ) -> str:
        interaction = await self._gemini_client.aio.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested description, no formatting, max 140 chars",
            input=f"""
                I have a spreadsheet to manage my finances, tracking income and expenses.
                Write a description for the '{sub_name}' sub-category under category '{cat_name}' for {transaction_type.name.lower()}, serving exclusively as a criteria to understand whether a certain transaction belongs to it.
            """,
        )
        return interaction.output_text

    async def _enrich_category(
        self, cat_name: str, subcats: list[str], transaction_type: TransactionType
    ) -> tuple[str, dict]:
        cat_task = self._generate_cat_descr(cat_name, subcats, transaction_type)
        sub_tasks = [self._generate_sub_descr(sub, cat_name, transaction_type) for sub in subcats]

        cat_descr, *sub_descrs = await asyncio.gather(cat_task, *sub_tasks)
        sub_dict = dict(zip(subcats, sub_descrs))

        return cat_name, {"description": cat_descr, "subcategories": sub_dict}

    async def _enrich_categories(
        self, categories_raw: dict[str, list[str]], transaction_type: TransactionType
    ) -> dict:
        tasks = [
            self._enrich_category(cat_name, subcats, transaction_type)
            for cat_name, subcats in categories_raw.items()
        ]
        results = await asyncio.gather(*tasks)
        return dict(results)

    async def write_categories(self):
        config.CATEGORIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        for transaction_type in [TransactionType.EXPENSE, TransactionType.INCOME]:
            json_path = (
                config.CATEGORIES_CACHE_DIR / f"{transaction_type.name.lower()[:3]}_cat.json"
            )
            reader = SheetReader()
            categories_raw = reader.get_categories_sheet(transaction_type)
            enriched_categories = await self._enrich_categories(categories_raw, transaction_type)
            with open(json_path, "w") as f:
                json.dump(enriched_categories, f, indent=2)

    def get_categories(self, transaction_type: TransactionType) -> dict:
        json_path = config.CATEGORIES_CACHE_DIR / f"{transaction_type.name.lower()[:3]}_cat.json"

        with open(json_path, "rt") as categories_file:
            return json.load(categories_file)


if __name__ == "__main__":
    builder = CategoriesBuilder()

    asyncio.run(builder.write_categories())
    exp_cat = builder.get_categories(TransactionType.EXPENSE)
    inc_cat = builder.get_categories(TransactionType.INCOME)

    print(exp_cat)
    print("\n\n")
    print(inc_cat)
