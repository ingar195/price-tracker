import logging
from alert import alerter
from db import SessionLocal, init_db
from models import Product, PricePoint
from scrape import fetch_html, extract_price
from logging_config import configure_logging

logger = logging.getLogger(__name__)


def track(url: str) -> None:
    html = fetch_html(url)
    product_name, price, in_stock, currency = extract_price(html, url)
    if price is None or product_name is None:
        logger.warning(f"Price or product name not found for {url}, skipping DB update.")
        return

    session = SessionLocal()
    # TODO: find-or-create Product, append a PricePoint, commit
    product = session.query(Product).filter_by(url=url).first()
    if not product:
        product = Product(url=url, title=product_name)
        session.add(product)
        session.commit()
        session.refresh(product)
        logger.info(f"Created new product: {product_name} ({url})")

    price_point = PricePoint(product_id=product.id, price=price, currency=currency, in_stock=in_stock)
    session.add(price_point)
    session.commit()
    session.close()
    logger.info(f"Saved price point for {product_name}: {price} {currency}")


def check_all_products() -> None:
    """Re-check every already-tracked product. Called on a schedule."""
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()

    logger.info(f"Scheduled check starting for {len(products)} product(s).")
    for product in products:
        try:
            track(product.url)

            if product.alert_type:
                session = SessionLocal()
                fetched = session.get(Product, product.id)
                if fetched is None:
                    session.close()
                    continue
                product = fetched
                points = product.price_points

                if len(points) >= 2 and points[-1].price < points[-2].price:
                    message = (
                        f"{product.title} price dropped: "
                        f"{points[-2].price} -> {points[-1].price} {points[-1].currency}"
                    )
                    alerter(product.alert_type, message)
                    logger.info(f"Alert sent for {product.title}")
                session.close()

        except Exception:
            logger.exception(f"Failed to check {product.url}")