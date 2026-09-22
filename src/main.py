import requests
import time
from pathlib import Path

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/ssuhaan-jaiin/flyrank_scraper)"
TIMEOUT = 10
CACHE_DIR = Path("cache")

CACHE_DIR.mkdir(exist_ok=True)


def fetch(url: str, cache_filename: str) -> str:
    cache_path = CACHE_DIR / cache_filename

    if cache_path.exists():
        print(f"CACHE HIT: {cache_filename}")
        return cache_path.read_text()

    print(f"FETCH: {url}")
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.status_code} for {url}")

    print(f"  -> status {response.status_code}, {len(response.text)} bytes")
    cache_path.write_text(response.text)
    return response.text


if __name__ == "__main__":
    html = fetch("https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
    print(f"Page 1 loaded, {len(html)} characters")


import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/ssuhaan-jaiin/flyrank_scraper)"
TIMEOUT = 10
CACHE_DIR = Path("cache")

CACHE_DIR.mkdir(exist_ok=True)


def fetch(url: str, cache_filename: str) -> str:
    cache_path = CACHE_DIR / cache_filename

    if cache_path.exists():
        print(f"CACHE HIT: {cache_filename}")
        return cache_path.read_text()

    print(f"FETCH: {url}")
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.status_code} for {url}")

    print(f"  -> status {response.status_code}, {len(response.text)} bytes")
    time.sleep(0.5)
    cache_path.write_text(response.text)
    return response.text


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


if __name__ == "__main__":
    urls = discover_book_urls()
