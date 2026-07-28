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
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
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
        
        product = None
        
        # Try to find Product in @graph
        if data.get("@graph"):
            for item in data["@graph"]:
                if item.get("mainEntity") and item["mainEntity"].get("@type") == "Product":
                    product = item["mainEntity"]
                    break
                # Check if item itself is a Product (power.no format)
                elif item.get("@type") == "Product":
                    product = item
                    break
        
        # Try direct Product type (for sites without @graph)
        if not product and data.get("@type") == "Product":
            product = data
        
        if not product:
            logger.debug("No Product JSON-LD found, skipping.")
            continue
        
        logger.debug(f"Extracted JSON-LD data: {product}")
        
        # Extract product info
        offers = product.get("offers")
        
        # Handle offers as array or object
        if isinstance(offers, list):
            offers = offers[0]  # Take first offer
        logger.debug(f"Extracted offers data: {offers}")
        price = float(offers.get("lowPrice") or offers["priceSpecification"][0].get("price"))
        product_name = product.get("name") or data.get("name")
        currency = offers.get("priceCurrency") or offers["priceSpecification"][0].get("priceCurrency")
        availability = offers.get("availability") or offers.get("availability")
        in_stock = ("InStock" in availability) if availability is not None else None
        
        logger.info(f"Extracted product info: {product_name}, {price}, {in_stock}, {currency}")
        return product_name, price, in_stock, currency
    
    # If we get here, no matching script was found
    raise ValueError("No valid Product JSON-LD found in page")

       
SCRAPERS = {
    "komplett.no": ld_json,
    "prisjakt.no": ld_json,
    "farmasiet.no": ld_json,
    "deal.no": ld_json,
    "multicom.no": ld_json,
    "apotekfordeg.no": ld_json,
    "power.no": ld_json,
    "elkjop.no": ld_json,
    "netonnet.no": ld_json,
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







