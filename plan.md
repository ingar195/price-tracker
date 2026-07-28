# Price Tracker & Alerter — Project Plan

> A learning project. The goal is not just a working app but understanding *why*
> each piece is built the way it is. Build in small, runnable steps.

## Goal

Paste a product URL from a supported site → the app tracks its price over time,
stores the history, and alerts me when it drops below a target. Adding support
for a new site should mean **one new file and nothing else changed**.

## Stack

| Concern        | Choice                        | Why |
|----------------|-------------------------------|-----|
| Language       | Python 3.11+                  | Comfortable with it; great scraping ecosystem |
| Web framework  | FastAPI                       | Async, small, excellent docs |
| Database       | SQLite + SQLAlchemy           | Zero setup; swap to Postgres later without rewriting queries |
| HTTP client    | httpx (async)                 | Modern, async-native |
| HTML parsing   | selectolax or BeautifulSoup   | Fast, simple |
| JS rendering   | Playwright (only if needed)   | Add later, only for sites that require it |
| Scheduling     | APScheduler                   | In-process re-check loop, no extra infra |
| UI             | Jinja2 templates + htmx       | Server-rendered; avoid React until it's justified |

## Architecture

```
User pastes URL
      │
      ▼
  Registry  ──finds──►  SiteScraper (per-site module)
      │                      │ fetch()
      ▼                      ▼
   Tracker  ◄── PriceResult ─┘
      │
      ├─► DB (append price_point)
      └─► Alert if price <= target

  Scheduler re-runs Tracker for all products on an interval.
```

### The core abstraction: site scrapers

Each supported site is a class subclassing `BaseScraper`. The base holds shared
behavior (HTTP with User-Agent, rate limiting, price parsing, URL matching); each
subclass only writes the part that's actually different — how to pull the price
out of *that* site's page.

```python
class BaseScraper:
    user_agent = "PriceTracker/1.0"
    domain: str
    def matches(self, url) -> bool: ...      # shared
    async def _get(self, url) -> str: ...    # shared HTTP + rate limit
    def _parse_price(self, text) -> float: ...  # shared
    async def fetch(self, url) -> PriceResult: ...  # per-site, the only real work
```

A registry auto-discovers every module in `scrapers/` so a new file self-registers.
**Extensibility test:** adding a site = copy a scraper file, change domain + `fetch`, done.

## Directory layout

```
pricetracker/
├── app/
│   ├── main.py            # FastAPI app + routes
│   ├── config.py          # settings (db path, interval, user-agent)
│   ├── db.py              # engine, session, init
│   ├── models.py          # SQLAlchemy tables
│   ├── scheduler.py       # APScheduler re-check loop
│   ├── tracker.py         # orchestration: fetch → save → maybe alert
│   ├── scrapers/
│   │   ├── __init__.py    # registry + auto-discovery
│   │   ├── base.py        # BaseScraper + PriceResult
│   │   ├── prisguide.py   # one site = one file
│   │   └── komplett.py
│   └── templates/
│       ├── index.html
│       └── product.html
├── tests/
│   └── test_scrapers.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Data model

Append-only history — never overwrite a price, always add a row.

- **products**: id, url, title, scraper_name, target_price, created_at
- **price_points**: id, product_id (fk), price, currency, in_stock, checked_at
- **alerts** (later): id, product_id (fk), triggered_at, price, notified

## Build order

Each step is independently runnable — get it working before moving on.

1. **One scraper, no web, no DB.** Script that takes a Komplett/Prisguide URL and
   prints the price. Parsing is the riskiest part — de-risk it first.
2. **Add SQLite.** Save each fetch as a `price_point`; confirm history accumulates.
3. **Formalize interface + registry.** Refactor step 1 into `BaseScraper`. Add the
   second site — this proves the abstraction holds.
4. **FastAPI + a page.** Paste URL → track it; list products with latest price.
5. **Scheduler.** APScheduler re-checks everything on an interval.
6. **Alerts.** When price ≤ target, notify (console/email first).
7. **History chart** in the UI.

## Things to watch

- **Check the Network tab before parsing HTML.** Prisguide/Komplett may expose a
  clean JSON endpoint that's far more stable than scraping markup.
- **Be a polite client:** real User-Agent, request delays, caching, respect
  `robots.txt` and each site's terms. Don't hammer them.
- **Some pages load prices via JavaScript.** If the price isn't in the raw HTML,
  that's the signal to either find the JSON call or (last resort) use Playwright.
- **Keep inheritance flat.** One `BaseScraper` + site subclasses. If tempted by a
  third layer, switch to composition/functions instead.

## Definition of done (v1)

- [ ] Paste a Prisguide or Komplett URL and it starts tracking
- [ ] Price history stored and viewable
- [ ] Scheduled re-checks running automatically
- [ ] Alert fires when price drops below target
- [ ] Adding a third site required exactly one new file
