# Price Tracker

A self-hosted price tracker: paste a product URL from a supported store, and it
periodically re-checks the price, keeps a full history, and sends a Discord
alert when the price drops.

Built as a learning project — the design favors clarity and easy extension
(adding a new store) over maximal features.

## Features

- **Web UI** to add/remove tracked products and pick an alert channel per product
- **Tested stores** (verified to work):
  - [Komplett](https://www.komplett.no)
  - [Prisjakt](https://www.prisjakt.no)
  - [Apotek For Deg](https://www.apotekfordeg.no)
  - [Power](https://www.power.no)
  - [Elkjøp](https://www.elkjop.no)
  - [NetOnNet](https://www.netonnet.no)
  - [Farmasiet](https://www.farmasiet.no)
  - [Deal](https://www.deal.no)
  - [Multicom](https://www.multicom.no)
  - **Plus any other site with JSON-LD product data** — even unlisted sites may work if they expose product info in the standard format
- **Price history** stored in SQLite, one row per check, never overwritten
- **Automatic re-checking** on a schedule (APScheduler), no manual refresh needed
- **Discord alerts** when a product's price drops compared to the previous check
- **New stores are cheap to add** — see [Adding a new site](#adding-a-new-site)

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) — web app / routes
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite — persistence
- [httpx](https://www.python-httpx.org/) + [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — fetching and parsing pages
- [APScheduler](https://apscheduler.readthedocs.io/) — background re-check loop
- Jinja2 templates — server-rendered UI, no frontend build step

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Copy the env template and fill in your own values:

```bash
cp .env_example .env
```

`.env` needs at minimum:

```
DISCORD_WEBHOOK_URL=<your Discord webhook URL>
```

`.env` is gitignored — never commit it. `.env_example` holds no real secrets and is safe to share.

## Running

```bash
uvicorn main:app --reload
```

Then open `http://localhost:8000`. On first run, the SQLite database
(`pricetracker.db`) and its tables are created automatically.

## Usage

1. Paste a product URL from a supported store into the input box and click **Add**.
2. The product appears with its current price. A background job re-checks all
   tracked products automatically (interval configurable via `CHECK_INTERVAL_MINUTES`
   in `.env`, default 60 minutes).
3. Pick **Discord** from a product's alert dropdown to get notified when its
   price drops below the previous check. Pick **Off** to disable.
4. **Delete** removes a product and its entire price history.

## How it works

```
Paste URL
   │
   ▼
extract_price() looks up the domain in the SCRAPERS registry (scrape.py)
   │
   ▼
matching parser pulls {title, price, in_stock, currency} from the page's
JSON-LD (<script type="application/ld+json">) data
   │
   ▼
tracker.track() finds-or-creates the Product row, appends a new PricePoint
   │
   ▼
if alert_type is set and the new price < the previous price → alerter()
sends a Discord message
```

A `BackgroundScheduler` job (`check_all_products`, wired up in `main.py`'s
`lifespan`) re-runs this for every tracked product on an interval, so prices
update without anyone visiting the site.

## Data model

- **`products`** — one row per tracked URL (`title`, `url`, `alert_type`, ...)
- **`price_points`** — one row per price check, linked to a product. Never
  updated in place, only appended — this is what gives you history for free.

## Adding a new site

Every supported site is one entry in the `SCRAPERS` dict in `scrape.py`:

```python
SCRAPERS = {
    "komplett.no": ld_json,
    "prisjakt.no": ld_json,
}
```

All current sites expose product data via JSON-LD, so they share the same `ld_json()` parser.

### To add a new site:

1. **Check if it has JSON-LD** — inspect the page source for a `<script type="application/ld+json">` block containing `"@type": "Product"`. 
2. **If yes** — just add the domain to `SCRAPERS` pointing at `ld_json`:
   ```python
   SCRAPERS = {
       ...
       "newsite.no": ld_json,
   }
   ```
3. **If no** — write a custom parser function with the same return shape `(title, price, in_stock, currency)` and point to it instead.

### Automatic fallback:

If a URL's domain is **not in `SCRAPERS`**, the app automatically tries the generic `ld_json` scraper anyway. This means you can track products from unlisted sites if they use JSON-LD structure — you don't need to update `SCRAPERS` first. Only add a domain to `SCRAPERS` if you've verified it works or want to explicitly support it.

No changes to `tracker.py`, `main.py`, or the database are needed to add a site.

## Project layout

```
main.py              FastAPI app: routes, scheduler wiring, static files
tracker.py           orchestration: fetch -> save -> maybe alert
scrape.py            per-site scrapers + the SCRAPERS registry
alert.py             alert delivery (currently: Discord webhook)
models.py            SQLAlchemy models (Product, PricePoint)
db.py                DB engine/session setup
config.py            loads .env, exposes settings
logging_config.py    logging setup (console + pricetracker.log)
templates/           Jinja2 templates (index.html)
static/               style.css
plan.md              original project plan / design notes
```

## Logging

All components log to both the console and `pricetracker.log`. Log level and
format are configured in `logging_config.py`.
