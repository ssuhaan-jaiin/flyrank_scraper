# The Polite Scraper

A small, polite scraping pipeline built for the FlyRank Internship Backend track (W5 · A9). It fetches the first 3 catalogue pages of [Books to Scrape](https://books.toscrape.com), visits all 60 book detail pages, and turns the raw HTML into clean, schema-validated JSON — surviving a broken page without crashing, and reporting exactly what happened on every run.

## Target classification

- **Site:** https://books.toscrape.com — a public sandbox built specifically for people to practice scraping on (confirmed on toscrape.com's own about page: "this is a website that exists solely to practice web scraping").
- **Scope:** the first 3 catalogue pages only (60 book listings total).
- **Data collected:** title, price, availability, star rating, description, and product URL for each book — all publicly shown catalogue data, nothing behind a login or paywall.
- **robots.txt result:** requested `https://books.toscrape.com/robots.txt` — returned `404 Not Found`. No robots file exists on this site. This is not treated as permission; it's simply the absence of a stated rule. Given the site's own explicit purpose (a practice sandbox), scraping the public catalogue pages within the stated 3-page scope is appropriate here regardless.
- I will not reuse this code on another site without checking its rules and terms first.

## Install & run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/main.py
```

Output lands in `output/books.json`, `output/errors.json`, and `output/run-report.json`. HTML is cached in `cache/` (git-ignored) so re-running during development doesn't re-hit the site.

## Record schema

Each entry in `books.json`:

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "...",
  "source_page": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "fetched_at": "2026-09-22T07:02:36.011467+00:00"
}
```

Validated with Pydantic before storage. Records that fail validation land in `errors.json` with a reason instead of `books.json`.

## Politeness rules followed

- Every real request sends an identifying user-agent: `FlyRankInternship-A9/1.0 (+https://github.com/ssuhaan-jaiin/flyrank_scraper)`.
- Every request has a 10-second timeout.
- At least 500ms between real requests (cached reads have no delay — they never leave the machine).
- Status code is checked before any HTML is touched.
- A `5xx` or timeout is retried once; a `404` or `403` is never retried.
- Development reads from `cache/` instead of re-requesting the live site.

## Why no browser was needed

The data needed (title, price, availability, rating, description) is already present in the HTML the server sends on first response — confirmed by viewing page source directly. A headless browser would only add startup cost and complexity for data that's already there in the plain HTTP response.

## Sample run report


  "start_time": "2026-09-22T07:06:31.696696+00:00",
  "duration_seconds": 126.09,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0,
  "failed_page_details": []
  
## Ethics note

This project only touches a public sandbox built explicitly for scraping practice. In general: prefer an official API when one exists, never bypass a login, paywall, or an explicit block, and collect only the data actually needed for the task at hand.

## Known limitation

Star ratings are read from a CSS class name (e.g. `class="star-rating Three"`) rather than a semantic data attribute — if the site's markup changes this specific pattern, rating extraction would silently break rather than fail loudly. A more robust version would validate the rating value against the known set (`One`–`Five`) and flag anything unexpected.