import json
from pathlib import Path

from google import genai

from carlobot import config
from carlobot.domain.types import TransactionType
from carlobot.sheets.reader import SheetReader


class CategoriesBuilder:
    _gemini_client = genai.Client()

    def __generate_cat_descr(self, cat_name: str, subcats: list[str], type: TransactionType) -> str:
        interaction = self._gemini_client.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested description, no formatting, max 140 chars",
            input=f"""
                    I have a spreadsheet to manage my finances, tracking income and expenses.
                    Write a description for the '{cat_name}' {type.name.lower()} category, serving exclusively as a criteria to understand whether a certain transaction belongs to it.
                    Keep into consideration also its subcategories: {', '.join(subcats)}
                """,
        )
        return interaction.output_text

    def __generate_sub_descr(self, sub_name: str, cat_name: str, type: TransactionType) -> str:
        interaction = self._gemini_client.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction="Only output the requested description, no formatting, max 140 chars",
            input=f"""
                I have a spreadsheet to manage my finances, tracking income and expenses.
                Write a description for the '{sub_name}' sub-category under category '{cat_name}' for {type.name.lower()}, serving exclusively as a criteria to understand whether a certain transaction belongs to it.
            """,
        )
        return interaction.output_text

    def __enrich_categories(self, categories_raw: dict[str, list[str]], type: TransactionType) -> dict:
        enriched = {}
        for cat_name, subcats in categories_raw.items():
            cat_descr = self.__generate_cat_descr(cat_name, subcats, type)
            sub_dict = {}
            for sub_name in subcats:
                sub_dict[sub_name] = self.__generate_sub_descr(sub_name, cat_name, type)

            enriched[cat_name] = {
                "description": cat_descr,
                "subcategories": sub_dict,
            }
        return enriched

    def write_categories(self):
        config.CATEGORIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        for type in [TransactionType.EXPENSE, TransactionType.INCOME]:
            json_path = config.CATEGORIES_CACHE_DIR / f"{type.name.lower()[:3]}_cat.json"

            try:
                with open(json_path, "xt") as categories_file:
                    reader = SheetReader()
                    categories_raw = reader.get_categories_sheet(type)
                    enriched_categories = self.__enrich_categories(categories_raw, type)
                    json.dump(enriched_categories, categories_file, indent=2)
            except FileExistsError:
                print(f"File {json_path.name} exists already, not generating anything")

    def get_categories(self, type: TransactionType) -> dict:
        json_path = config.CATEGORIES_CACHE_DIR / f"{type.name.lower()[:3]}_cat.json"

        with open(json_path, "rt") as categories_file:
            return json.load(categories_file)


if __name__ == "__main__":
    builder = CategoriesBuilder()

    builder.write_categories()
    exp_cat = builder.get_categories(TransactionType.EXPENSE)
    inc_cat = builder.get_categories(TransactionType.INCOME)

    print(exp_cat)
    print("\n\n")
    print(inc_cat)
