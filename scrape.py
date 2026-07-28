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
    """
    logger.debug("Searching for <script type='application/ld+json'> tags.")
    scripts = soup.find_all("script", type="application/ld+json")
    
    for script in scripts:
        logger.debug(f"Found <script type='application/ld+json'>: {script.string[:100]}...")
        data = json.loads(script.string)
        logger.debug(f"Root @type: {data.get('@type')}, has @graph: {bool(data.get('@graph'))}")
        
        # Skip if it's not a Product and has no @graph
        if data.get("@type") != "Product" and not data.get("@graph"):
            logger.debug("Not a Product JSON-LD or missing @graph, skipping.")
            continue
        
        # If @graph exists, extract mainEntity
        if data.get("@graph"):
            data = data["@graph"][0]["mainEntity"]
        
        logger.debug(f"Extracted JSON-LD data: {data}")
        
        # Extract product info
        offers = data["offers"]
        price = float(offers.get("lowPrice") or offers["price"])
        product_name = data.get("name")
        currency = offers.get("priceCurrency")
        availability = offers.get("availability")
        in_stock = ("InStock" in availability) if availability is not None else None
        
        logger.info(f"Extracted product info: {product_name}, {price}, {in_stock}, {currency}")
        return product_name, price, in_stock, currency
    
    # If we get here, no matching script was found
    raise ValueError("No valid Product JSON-LD found in page")


# def prisjakt_price_scraper(soup) -> tuple[str, float, bool, str]:
#     scripts = soup.find_all("script", type="application/ld+json")
#     for script in scripts:        
#         data = json.loads(script.string)   
#         if data.get("@type") != "Product":
#                 continue
        
SCRAPERS = {
    "komplett.no": ld_json,
    "prisjakt.no": ld_json,
    "farmasiet.no": ld_json,
    "deal.no": ld_json,
    "multicom.no": ld_json,
    "apotekfordeg.no": ld_json,
}
def extract_price(html: str, url: str) -> tuple[str, float, bool | None, str]:
    soup = BeautifulSoup(html, "html.parser")
    logger.debug(f"Extracting price from {url}")

    for domain, scraper in SCRAPERS.items():
        if domain in url:
            logger.debug(f"{domain} page detected.")
            product_name, price, in_stock, currency = scraper(soup)
            product_name = unescape(product_name)
            logger.info(f"Found product: {product_name}, price: {price}, in stock: {in_stock}, currency: {currency}")
            return product_name, price, in_stock, currency
    
    # Domain not in SCRAPERS list, try generic ld_json scraper as fallback
    logger.warning(f"Domain not in SCRAPERS list, trying generic scraper: {url}")
    product_name, price, in_stock, currency = ld_json(soup)
    product_name = unescape(product_name)
    logger.info(f"Found product: {product_name}, price: {price}, in stock: {in_stock}, currency: {currency}")
    return product_name, price, in_stock, currency







