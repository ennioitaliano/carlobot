# CarloBot

Track income and expenses in Google Sheets with a text or voice message on Telegram.

Tell CarloBot what you spent or earned. He extracts the details, picks a category from your spreadsheet, and adds the transaction to the current month's tab.

![CarloBot recording a transaction from Telegram in Google Sheets](https://raw.githubusercontent.com/ennioitaliano/carlobot/main/demo.gif)

## Intro

CarloBot turns a natural-language message into a spreadsheet row containing a date, an amount, a short description, and a classification.

For example, send a message such as:

> Ieri ho speso 25 euro per una pizza.

Carlo identifies an expense, extracts yesterday's date and the amount, generates a brief description in Italian, and assigns a category and subcategory from your workbook. He then writes the transaction to Google Sheets and reports the result in Telegram.

Voice messages follow the same flow after transcription. Transactions are written automatically: there is no confirmation step before saving.

## How it works

| Task | Service |
| --- | --- |
| Transcribe voice messages | Gemini `gemini-3.5-transcribe` |
| Classify a message as income, expense, or not a transaction | TypeSafe system-one API (jev) |
| Detect whether a message includes a date | TypeSafe system-one API |
| Extract a date, amount, and description | Gemini `gemini-3.1-flash-lite` |
| Generate classification criteria from your categories | Gemini `gemini-3.1-flash-lite` |
| Choose a category and subcategory | TypeSafe system-one API |
| Read categories and append transactions | Google Sheets API |

Category criteria are generated on the first run and cached locally. Later runs reuse them; `/refresh_categories` rebuilds them from the spreadsheet.

## Setup

You need Python 3.12 or newer with `pip` and `venv`, a Google account, a Telegram bot token, and API keys for Gemini and TypeSafe. API access, quotas, and costs depend on your provider accounts.

### Step 1. Get the code

```bash
git clone https://github.com/ennioitaliano/carlobot.git
cd carlobot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
```

### Step 2. Prepare your workbook

Open the [Google Sheets template](https://docs.google.com/spreadsheets/d/1xt3y_rWZdBy9c95X1Ami8Suydsk-Nmbp3t2BmL4VewY/edit?usp=sharing) and choose **File → Make a copy**. Use your copy's ID when configuring `GOOGLE_SHEET_ID`.

The template includes monthly tabs, a `config` tab for categories, and a `bilancio` summary tab. Keep tab names unchanged.

The column order is fixed:

| Table | Columns, in order |
| --- | --- |
| Expenses | Date, Amount, Description, Category, Subcategory |
| Income | Date, Amount, Description, Subcategory |

Income categories are used during classification, but only the subcategory is written to the income table.

Correct ranges for expenses/income categories and transactions are already filled in `.env.example`. You can customize categories in the `config` tab; use your own category names and give every category at least one subcategory. Keep the template's formulas, named ranges, and validation rules consistent if you change its structure.

### Step 3. Connect Google Sheets

The bot authenticates with a Google service account.

The service account JSON key is required.

1. In [Google Cloud Console](https://console.cloud.google.com/), select or create a project and enable the **Google Sheets API**.
2. Create a service account and download a JSON key for it.
3. Save the key as `google_service_account.json` in the repository root, matching the prefilled path in `.env.example`. Alternatively, store it elsewhere and set `GOOGLE_SERVICE_ACCOUNT_FILE` to its absolute path. JSON files are ignored by Git.
4. Share your workbook with the key's `client_email` address, granting **Editor** access so the bot can append transactions.

### Step 4. Get your bot token and API keys

- Create a Telegram bot through [BotFather](https://t.me/BotFather) and copy its token. You can restrict its usage in BotFather so that only you can interact with it. 
- Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).
- Obtain a TypeSafe API key from [TypeSafe](https://typesafe.ai/).

### Step 5. Configure `.env.local`

```bash
cp .env.example .env.local
```

Fill in the credentials and your copy's spreadsheet ID. Keep the prefilled ranges when using the template:

```dotenv
TG_BOT_TOKEN=your_telegram_bot_token
TYPESAFE_API_KEY=your_typesafe_api_key
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=./google_service_account.json
EXPENSE_CATEGORIES_RANGE=config!C4:K
INCOME_CATEGORIES_RANGE=config!P4:R
EXPENSE_INSERT_RANGE=!B3:F
INCOME_INSERT_RANGE=!H3:K
```

| Variable | What it controls |
| --- | --- |
| `TG_BOT_TOKEN` | Telegram bot authentication |
| `TYPESAFE_API_KEY` | TypeSafe classification API access |
| `GEMINI_API_KEY` | Gemini extraction and transcription API access |
| `GOOGLE_SHEET_ID` | Your copy's ID in `docs.google.com/spreadsheets/d/<ID>/edit` |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to the service account JSON key; prefilled as `./google_service_account.json`. Relative paths are resolved from the repository root. |
| `EXPENSE_CATEGORIES_RANGE` | Category and subcategory columns for expenses, including their first row |
| `INCOME_CATEGORIES_RANGE` | Category and subcategory columns for income, including their first row |
| `EXPENSE_INSERT_RANGE` | Expense table range suffix, appended to the current month's tab name |
| `INCOME_INSERT_RANGE` | Income table range suffix, appended to the current month's tab name |

For example, in October, `EXPENSE_INSERT_RANGE=!B3:F` becomes `Oct!B3:F`. Google Sheets appends the row to the table in that range.

`.env.local` and `data/` are ignored by Git. Keep tokens and service account keys private.

### Step 6. Run the bot

From the repository root, with the virtual environment active:

```bash
python -m carlobot
```

On the first run, Carlo reads your categories and generates their classification criteria. Wait for this initialization before sending transactions: messages received before the parser is ready are ignored. Subsequent runs load the cached criteria from `data/categories/`.

The bot uses polling. Keep the process running to receive messages; no public web server is required.

## Usage

Open your bot's chat in Telegram and send one transaction per text or voice message. For example:

> Ho speso 42 euro al supermercato.

> Oggi ho ricevuto 1500 euro di stipendio.

Carlo replies with the extracted details and reports when the row has been written to Google Sheets.

| Command | Action |
| --- | --- |
| `/debug` | Toggle detailed parsing output, including classification confidence values, for your user |
| `/refresh_categories` | Read categories from the workbook again and regenerate their classification criteria |

Use `/refresh_categories` after editing category names or subcategories. Existing transaction rows are not reclassified.

## Current limits and data handling

- **Current month only.** Dates are interpreted using `Europe/Rome`. A message without a date uses today; an extracted date outside the current month and year is rejected.
- **Euro display.** Telegram summaries show amounts in euros. The bot does not extract a currency field or convert currencies.
- **Italian descriptions.** Generated descriptions are requested in Italian, with a maximum of three words.
- **Automatic writes.** There is no approval or duplicate-detection step. Sending the same transaction again can create another row; correct mistakes directly in the sheet.
- **Bot access.** The current code has no Telegram user or chat allowlist. Anyone able to message the bot can trigger processing and writes to the configured workbook.
- **External processing.** Telegram carries your messages; voice recordings go to Gemini for transcription. Message text is processed by Gemini and TypeSafe. Category names and subcategories are sent to Gemini to generate classification criteria, which are then used by TypeSafe.
- **Local state.** The `data/` directory stores category criteria and Telegram persistence, including user debug preferences. Transaction rows are stored in Google Sheets.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Startup reports a missing environment variable | Fill in all required entries in `.env.local` and run from the repository root. |
| The service account key cannot be loaded | Set `GOOGLE_SERVICE_ACCOUNT_FILE` to an existing JSON key file; do not leave it empty. |
| Google Sheets reports a permission error | Enable the Sheets API and share the correct workbook with the service account as Editor. |
| A range cannot be read or written | Check tab names, range syntax, and the current month's tab. |
| Categories are empty or outdated | Check the category ranges and column layout, then run `/refresh_categories`. |
| The bot ignores messages just after its first startup | Allow category initialization to finish and check the terminal for errors. |
| A transaction date is rejected | Use a date within the current month and year in `Europe/Rome`. |
| An AI request fails | Check API keys, model access, and provider quotas. |

## License

Released under the [MIT license](LICENSE). Developed by [Ennio Italiano](https://github.com/ennioitaliano).
