# CarloBot
Insert expense/income in Google Sheets by sending natural-language, audio or text message on Telegram.

## Current Features

Send a natural-language, text-only message to Carlo, and he will reply with:

- **Transaction type classification**, using [jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) to tell if the specified transaction is an expense or income one.
- **Category and sub-category classification,** using jev to assign the transaction to the correct category and sub-category; criteria to choose categories are described using Gemini 3.1 Flash-Lite only once at the start of the system.
- **Amount detection**, using Gemini 3.1 Flash-Lite to extract the amount of the transaction from the message.
