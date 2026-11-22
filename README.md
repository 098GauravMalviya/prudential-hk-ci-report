# Hong Kong insurance competitive-intelligence monitor (code)

This repository holds the code behind a competitive-intelligence monitor that compares four insurers in Hong Kong: Prudential, AIA, Manulife and AXA. It collects public data, classifies it into an evidence database, builds an interactive report page with filters, and serves that page behind a login with an "Ask the report" chat.

**What this repository holds:** code only.

**What it leaves out:**
- the client report itself (its text and curated tables)
- the chat knowledge base
- the collected data and the evidence database
- licensed data
- narration audio
- all keys and passwords

## Folders

| Folder | What it does |
|---|---|
| `pipeline/` | Collects public data and builds the evidence database (`pipeline/`); runs one-off collectors such as Google Maps footprint, HKEX filings, social media and translation (`tools/`). The technical reference is `docs/TECHNICAL_DOCUMENTATION.md`. |
| `report_builder/` | Builds the report page and the chat knowledge base from the database (`build.py`). Also includes the investor, social, location and narration modules, plus link checkers. |
| `app/` | The deployable web app (Vercel, Python): a password-protected entry point (`api/index.py`) and the chat backend (`backend.py`). |

## Running it

You need Python 3.11. Put your own keys in a `.env` file at the project root; it is git-ignored and never committed. The variables are:

| Variable | What it is for |
|---|---|
| `APIFY_TOKEN` | Apify actors |
| `EXA_API_KEY`, `TAVILY_API_KEY` | Web search |
| `GEMINI_API_KEY` | Chat and translation |
| `ELEVENLABS_API_KEY` | Optional: narration |

The app reads two more variables, `REPORT_USERNAME` and `REPORT_PASSWORD`. Set them only as server-side environment variables on the host, never in code.

`report_builder/build.py` also needs the report content files (`body.html`, `data.js`, `dashboard.js`) and a collected database. Neither is published here.

## Updates (22 Nov 2026)

- `report_builder/`: front-end modules for the redesigned report (overview, charts at the top, module cards, image-first cards and detail panel, geo footprint, captures wall, mainland social conversation from Xiaohongshu and WeChat, findings explorer, theme CSS).
- `pipeline/tools/`: new collectors for Android reviews, IA market share, HK media sites, news and evidence images, page captures and title translation.
- `pipeline/tools/scrape_prudential_newsroom.py` reads press-office contacts from `media_contacts.local.json` (git-ignored) rather than from code.

## Data handling

- Public sources only.
- No logins are bypassed and robots.txt is respected.
- Licensed data is labelled as such and never redistributed.
- Personal contact details are stripped from collected text and kept out of this repository.
