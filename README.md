# CarloBot
Insert expense/income in Google Sheets by sending natural-language, audio or text message on Telegram.

## Current Features

Send a natural-language, text-only message to Carlo, and he will reply with:

- **Transaction type classification:** telling you if the specified transaction is an expense or income one, using [jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- **Category and sub-category classification:** telling you to which category and sub-category the transaction belongs to. Jev is used again to classify the transaction into categories; criteria to choose are described using Gemini 3.1 Flash-Lite only once at the start of the system.
