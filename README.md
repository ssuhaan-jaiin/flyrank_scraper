# Books to Scrape — polite scraper

## Target classification

- **Site:** https://books.toscrape.com — a public sandbox built specifically for people to practice scraping on (confirmed on toscrape.com's own about page: "this is a website that exists solely to practice web scraping").
- **Scope:** the first 3 catalogue pages only (60 book listings total).
- **Data collected:** title, price, availability, star rating, description, and product URL for each book — all publicly shown catalogue data, nothing behind a login or paywall.
- **robots.txt result:** requested `https://books.toscrape.com/robots.txt` — returned `404 Not Found`. No robots file exists on this site. This is not treated as permission; it's simply the absence of a stated rule. Given the site's own explicit purpose (a practice sandbox), scraping the public catalogue pages within the stated 3-page scope is appropriate here regardless.
- I will not reuse this code on another site without checking its rules and terms first.
