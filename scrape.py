import sys
import json
import httpx
import logging
from html import unescape
from bs4 import BeautifulSoup
from db import SessionLocal, init_db
from models import Product, PricePoint

logger = logging.getLogger(__name__)


def fetch_html(url: str) -> str:
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PriceTracker/0.1"}
    resp = httpx.get(url, headers=HEADERS, timeout=10.0, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def ld_json(soup) -> tuple[str, float, bool | None, str]:
    """
    Using the <script type="application/ld+json"> tag, extract product info.

    Extracts:
    * product name
    * price
    * stock status
    * currency

    Supported stores:
    * Komplett
    * Prisjakt
    """
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:        
        data = json.loads(script.string)   # parse the text inside <script> as JSON
        if data.get("@type") != "Product":
                continue
        
        offers = data["offers"]
        price = float(offers.get("lowPrice") or offers["price"]) # Lowest price for Prisjakt, single price for Komplett
        product_name = data["name"]
        currency = data["offers"]["priceCurrency"]
        availability = offers.get("availability")
        in_stock = ("InStock" in availability) if availability is not None else None


        break # we found the product, no need to continue
    return product_name, price, in_stock, currency


# def prisjakt_price_scraper(soup) -> tuple[str, float, bool, str]:
#     scripts = soup.find_all("script", type="application/ld+json")
#     for script in scripts:        
#         data = json.loads(script.string)   
#         if data.get("@type") != "Product":
#                 continue
        
SCRAPERS = {
    "komplett.no": ld_json,
    "prisjakt.no": ld_json,
}
def extract_price(html: str, url: str) -> tuple[str, float, bool | None, str]:
    soup = BeautifulSoup(html, "html.parser")    

    for domain, scraper in SCRAPERS.items():
        if domain in url:
            logger.debug(f"{domain} page detected.")
            product_name, price, in_stock, currency = scraper(soup)
            product_name = unescape(product_name)            
            break
    else:
        logger.error(f"Domain not supported: {url}")
        raise ValueError(f"Domain {url} not supported.")

    if price is None:
        logger.error(f"Price not found in the JSON data for {url}")
        raise ValueError("Price not found in the JSON data.")
    if product_name is None:
        logger.error(f"Product name not found in the JSON data for {url}")
        raise ValueError("Product name not found in the JSON data.")
    logger.info(f"Found product: {product_name}, price: {price}, in stock: {in_stock}, currency: {currency}")

    return product_name, price, in_stock, currency







