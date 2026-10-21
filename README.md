# CarloBot
Insert expense/income in Google Sheets by sending natural-language, audio or text message on Telegram.

![](https://github.com/ennioitaliano/carlobot/blob/develop/demo.gif)

## Current Features

When I send a natural-language, text or voice messages to Carlo, he replies with:

- **Transaction type classification**, using [jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) to tell if the specified transaction is an expense or income one.
- **Date detection**, using jev to detect if a date/timing indication is present in the message and Gemini to extract it.
- **Amount detection**, using Gemini to extract the amount of the transaction from the message.
- **Description detection**, using Gemini to extract a brief description of 3 word max.
- **Category and sub-category classification,** using jev to assign the transaction to the correct category and sub-category (which are defined in the spreadsheet itself); criteria to choose categories are described using Gemini 3.1 Flash-Lite only once at the start of the system.

Then, he actually inserts the transaction record in the correct row of my spreadsheet.
