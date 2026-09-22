import re
import json
import requests
import time
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Optional

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/ssuhaan-jaiin/flyrank_scraper)"
TIMEOUT = 10
CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("output")

CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

stats = {"fetches": 0, "cache_hits": 0}


class FetchError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str


def fetch(url: str, cache_filename: str) -> str:
    cache_path = CACHE_DIR / cache_filename

def fetch(url: str, cache_filename: str) -> str:
    cache_path = CACHE_DIR / cache_filename

    if cache_path.exists():
        print(f"CACHE HIT: {cache_filename}")
        stats["cache_hits"] += 1
        return cache_path.read_text(encoding="utf-8")

    for attempt in (1, 2):
        try:
            print(f"FETCH: {url} (attempt {attempt})")
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
            response.encoding = "utf-8"
        except requests.exceptions.Timeout:
            if attempt == 1:
                print("  -> timeout, retrying once")
                time.sleep(1)
                continue
            raise FetchError(f"Timeout after retry: {url}")

        if response.status_code == 200:
            print(f"  -> status 200, {len(response.text)} bytes")
            stats["fetches"] += 1
            time.sleep(0.5)
            cache_path.write_text(response.text)
            return response.text

        if response.status_code in (404, 403):
            raise FetchError(f"{response.status_code} for {url}", status_code=response.status_code)

        if response.status_code >= 500 and attempt == 1:
            print(f"  -> {response.status_code}, retrying once")
            time.sleep(1)
            continue

        raise FetchError(f"{response.status_code} for {url}", status_code=response.status_code)

    raise FetchError(f"Failed after retries: {url}")


def discover_book_urls():
    base_url = "https://books.toscrape.com/catalogue/page-1.html"
    page_url = base_url
    page_num = 1
    max_pages = 3
    all_urls = []

    while page_num <= max_pages:
        cache_filename = f"catalogue-page-{page_num}.html"
        html = fetch(page_url, cache_filename)
        soup = BeautifulSoup(html, "html.parser")

        for article in soup.select("article.product_pod"):
            relative_href = article.select_one("h3 a")["href"]
            absolute_url = urljoin(page_url, relative_href)
            all_urls.append(absolute_url)

        next_link = soup.select_one("li.next a")
        if next_link is None or page_num == max_pages:
            break

        page_url = urljoin(page_url, next_link["href"])
        page_num += 1

    unique_urls = list(dict.fromkeys(all_urls))

    print(f"catalogue_pages={page_num}")
    print(f"discovered={len(all_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls


def extract_book(url: str, source_page: str) -> dict:
    cache_filename = url.rstrip("/").split("/")[-2] + ".html"
    html = fetch(url, cache_filename)
    soup = BeautifulSoup(html, "html.parser")

    product_main = soup.select_one("div.product_main")
    title = product_main.select_one("h1").get_text(strip=True)

    price_text = soup.select_one("p.price_color").get_text(strip=True)
    availability_text = soup.select_one("p.availability").get_text(strip=True)

    rating_tag = product_main.select_one("p.star-rating")
    rating_text = rating_tag["class"][1] if rating_tag else None

    description_tag = soup.select_one("#product_description")
    if description_tag:
        description = description_tag.find_next_sibling("p").get_text(strip=True)
    else:
        description = None

    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


def parse_price(price_text: str) -> float:
    match = re.search(r"[\d.]+", price_text)
    return float(match.group())


def normalize_and_validate(raw_records: list) -> tuple:
    seen_urls = {}
    valid = []
    errors = []

    for raw in raw_records:
        url = raw["product_url"]

        if url in seen_urls:
            continue
        seen_urls[url] = True

        try:
            raw_with_price = {**raw, "price_gbp": parse_price(raw["price_text"])}
            record = BookRecord(**raw_with_price)
            valid.append(json.loads(record.model_dump_json()))
        except (ValidationError, ValueError) as e:
            errors.append({"url": url, "reason": str(e)})

    return valid, errors


if __name__ == "__main__":
    start_time = datetime.now(timezone.utc)

    urls = discover_book_urls()

    # TEST ONLY — uncomment the next line to prove Stage 5's failure handling,
    # then comment it back out before your real/final run.
    # urls.append("https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html")

    raw_records = []
    failed_pages = []

    for url in urls:
        try:
            record = extract_book(url, source_page=url)
            raw_records.append(record)
        except FetchError as e:
            print(f"FAILED: {url} -> {e}")
            failed_pages.append({"url": url, "reason": str(e)})

    print(f"detail_pages_ok={len(raw_records)}")

    valid_records, errors = normalize_and_validate(raw_records)

    (OUTPUT_DIR / "books.json").write_text(json.dumps(valid_records, indent=2))
    (OUTPUT_DIR / "errors.json").write_text(json.dumps(errors, indent=2))

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    run_report = {
        "start_time": start_time.isoformat(),
        "duration_seconds": round(duration, 2),
        "pages_fetched": stats["fetches"],
        "cache_hits": stats["cache_hits"],
        "valid_records": len(valid_records),
        "invalid_records": len(errors),
        "failed_pages": len(failed_pages),
        "failed_page_details": failed_pages
    }
    (OUTPUT_DIR / "run-report.json").write_text(json.dumps(run_report, indent=2))

    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"failed_pages={len(failed_pages)}")