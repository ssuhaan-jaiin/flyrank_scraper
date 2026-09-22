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