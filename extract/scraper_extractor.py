import json
import logging
import os
import time
from argparse import ArgumentParser
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def mainpage_product_details(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Image URL
    img_tag = soup.select_one('span[data-component-type="s-product-image"] img.s-image')
    product_img_url = img_tag["src"] if img_tag else None

    # Product Name
    try:
        name = soup.find("h2").find("span").get_text(strip=True)
    except Exception:
        name = None

    # Price and Currency
    try:
        price_tag = soup.select_one(".a-price .a-offscreen")
        if price_tag:
            price_text = price_tag.get_text(strip=True)
            print(price_tag)
            parts = price_text.split()
            currency, price = parts if len(parts) == 2 else ("", parts[0])
        else:
            currency, price = None, None
    except Exception:
        currency, price = None, None

    return {
        "name": name,
        "price": price,
        "currency": currency,
        "image_url": product_img_url,
    }


def extract_product_data(page, page_url, starting_index=1):
    elements = page.query_selector_all("div.a-section.a-spacing-base")
    product_data = []
    today = datetime.today().strftime("%Y-%m-%d")

    for idx, el in enumerate(elements, start=starting_index):
        try:
            html = el.inner_html()
            details = mainpage_product_details(html)

            link = el.query_selector("a.a-link-normal")
            href = link.get_attribute("href") if link else None

            if href:
                details.update(
                    {
                        "link": f"https://www.amazon.co.za{href}",
                        "page_url": page_url,
                        "marketplace_name": "www.amazon.co.za",
                        "index": idx,
                        "date_collected": today,
                    }
                )
                product_data.append(details)
        except Exception as e:
            print(f"Skipping product #{idx} due to error: {e}")

    return product_data


def save_product_data_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"\nSaved {len(data)} product items to {filename}")


def extract_all_paginated_data(paginated_urls):
    all_product_data = []
    global_index = 1

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        for page_number, url in enumerate(paginated_urls, start=1):
            for attempt in range(5):
                try:
                    print(
                        f"\nExtracting page {page_number}: {url} (Attempt {attempt + 1})"
                    )
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_load_state("networkidle")

                    page_data = extract_product_data(page, url, global_index)
                    all_product_data.extend(page_data)
                    global_index += len(page_data)
                    break
                except Exception as e:
                    print(f"Error on page {page_number}, attempt {attempt + 1}: {e}")
                    time.sleep(3)

        browser.close()

    return all_product_data


def get_max_page_number(url: str) -> int:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_load_state("networkidle")

        elements = page.query_selector_all("span.s-pagination-item")
        max_page = max(
            (
                int(el.inner_text().strip())
                for el in elements
                if el.inner_text().strip().isdigit()
            ),
            default=1,
        )
        browser.close()
        return max_page


def build_url(template: str, page_index: int) -> str:
    return template.format(page_index=page_index)


def main():
    parser = ArgumentParser()
    parser.add_argument("--path", required=True, help="Output folder")
    parser.add_argument("--name", required=True, help="Output filename")
    parser.add_argument("--url", required=True, help="URL template with {page_index}")
    parser.add_argument("--min", type=int, default=1, help="Minimum page number")
    parser.add_argument("--max", type=int, help="Maximum page number limit")

    args = parser.parse_args()
    os.makedirs(args.path, exist_ok=True)

    actual_max = get_max_page_number(build_url(args.url, 1))
    max_page = min(args.max, actual_max) if args.max else actual_max

    logger.info("Max paginated number found: %s", actual_max)
    logger.info("Selected paginated number: %s", max_page)
    paginated_urls = [build_url(args.url, i) for i in range(args.min, max_page + 1)]

    all_products = extract_all_paginated_data(paginated_urls)
    save_product_data_to_json(all_products, filename=args.name)


if __name__ == "__main__":
    main()
