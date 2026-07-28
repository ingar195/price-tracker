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
        logger.debug(f"Found <script type='application/ld+json'>: {script.string[:100]}...")  # log first 100 chars
        data = json.loads(script.string)
        logger.debug(f"Root @type: {data.get('@type')}, has @graph: {bool(data.get('@graph'))}")
        if data.get("@type") != "Product" and not data.get("@graph"):
                logger.debug("Not a Product JSON-LD or missing @graph, skipping.")
                continue
        logger.debug(f"Found Product JSON-LD data: {data}")
        if data.get("@graph"):
            data = data["@graph"][0]["mainEntity"]
        
        logger.debug(f"Extracted JSON-LD data: {data}")
        offers = data["offers"]
        logger.debug(f"Offers: {offers}")
        price = float(offers.get("lowPrice") or offers["price"]) # Lowest price for Prisjakt, single price for Komplett
        logger.debug(f"Price: {price}")
        product_name = data.get("name") or offers.get("name") or data.get("name")
        logger.debug(f"Product name: {product_name}")
        currency = offers.get("priceCurrency")
        logger.debug(f"Currency: {currency}")
        availability = offers.get("availability")
        logger.debug(f"Availability: {availability}")
        in_stock = ("InStock" in availability) if availability is not None else None
        logger.debug(f"In stock: {in_stock}")
        break # we found the product, no need to continue
    logger.info(f"Extracted product info: {product_name}, {price}, {in_stock}, {currency}")
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
            break
            
    else:
        logger.error(f"Domain not supported: {url}")
        try: 
            logger.debug(f"Domain not detected in supported list but trying ld_json scraper anyway.")
            product_name, price, in_stock, currency = ld_json(soup)
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise ValueError(f"Domain {url} not supported.")

    if price is None:
        logger.error(f"Price not found in the JSON data for {url}")
        raise ValueError("Price not found in the JSON data.")
    if product_name is None:
        logger.error(f"Product name not found in the JSON data for {url}")
        raise ValueError("Product name not found in the JSON data.")
    logger.info(f"Found product: {product_name}, price: {price}, in stock: {in_stock}, currency: {currency}")

    return product_name, price, in_stock, currency







