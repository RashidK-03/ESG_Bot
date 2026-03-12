# ESG Regulatory Updates Bot

A Telegram bot for monitoring changes in international and national ESG regulations and sustainable development standards. The bot automatically tracks updates from key ESG sources and delivers AI-generated summaries to subscribed users.

## Features

- 📡 **Multi-source monitoring** — tracks 6 ESG sources automatically
- 🤖 **AI-powered summaries** — generates structured analysis via OpenAI GPT-4o-mini
- 🗓️ **Weekly auto-check** — automatically sends new updates every week
- 🔍 **On-demand search** — check any source instantly via commands
- 🗄️ **Deduplication** — each user only receives updates they haven't seen before

## Sources

| Source | Region | Method |
|--------|--------|--------|
| [ISSB (ifrs.org)](https://www.ifrs.org/news-and-events/news/) | Global | Playwright (JS rendering) |
| [GRI](https://www.globalreporting.org/news/news-center/) | Global | HTTP parsing |
| [EU Commission](https://ec.europa.eu/commission/presscorner/) | EU | RSS feed |
| [AIFC](https://aifc.kz/news/) | Kazakhstan | RSS feed |
| [AFSA](https://afsa.aifc.kz/news/) | Kazakhstan | RSS feed |
| [GFC AIFC](https://gfc.aifc.kz/en/news) | Kazakhstan | HTTP parsing |

## Project Structure

```
esgbot/
├── bot.py              # Telegram bot — commands and handlers
├── checker.py          # Orchestrates all sources, ESG filtering
├── database.py         # SQLite — deduplication per user
├── summarizer.py       # OpenAI GPT-4o-mini summary generation
├── config.py           # Loads environment variables
├── main.py             # Entry point
├── scheduler.py        # Scheduled jobs logic
├── sources/
│   ├── issb.py         # ISSB parser (Playwright + fallback)
│   ├── gri.py          # GRI parser
│   ├── eu_commission.py# EU Commission RSS
│   ├── kazakhstan.py   # AIFC, AFSA, GFC parsers
│   └── rss_source.py   # Generic RSS fetcher
├── .env                # Secret keys (not committed to git)
├── .env.example        # Example env file for new users
├── requirements.txt    # Python dependencies
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/RashidK-03/ESG_Bot.git
cd ESG_Bot
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

- **BOT_TOKEN** — get from [@BotFather](https://t.me/BotFather) on Telegram
- **OPENAI_API_KEY** — get from [platform.openai.com](https://platform.openai.com)

### 5. Run the bot

```bash
python main.py
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and subscribe to weekly updates |
| `/check` | Check all sources for new updates right now |
| `/news issb` | Latest ISSB news |
| `/news gri` | Latest GRI news |
| `/news eu` | Latest EU Commission news |
| `/news kz` | Latest Kazakhstan ESG news |
| `/help` | Show help message |

## How It Works

1. User sends `/start` — bot registers them and starts a weekly job
2. Every 7 days the bot automatically checks all sources
3. New updates are filtered by ESG keywords
4. Each update is checked against the database (per user deduplication)
5. New updates are summarized by GPT-4o-mini and sent to the user

## Requirements

- Python 3.10+
- Telegram Bot Token
- OpenAI API Key

## Tech Stack

- `python-telegram-bot` — Telegram bot framework
- `playwright` — headless browser for JS-rendered pages
- `beautifulsoup4` + `requests` — HTML parsing
- `feedparser` — RSS feed parsing
- `openai` — AI summary generation
- `sqlite3` — local database for deduplication
