import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore

from db import SessionLocal, init_db
from models import Product

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from tracker import track, check_all_products
from logging_config import configure_logging
from config import ALERT_TIMER

configure_logging()
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # ensure DB tables exist before the scheduler can use them
    scheduler.add_job(check_all_products, "interval", minutes=ALERT_TIMER)  # every 60 minutes
    scheduler.start()
    logger.info(f"Scheduler started: checking all products every {ALERT_TIMER} minutes.")
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped.")


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request):
    session = SessionLocal()
    products = session.query(Product).all()
    result = []
    for p in products:
        latest = p.price_points[-1] if p.price_points else None
        result.append({
            "id": p.id,
            "title": p.title,
            "url": p.url,
            "latest_price": latest.price if latest else None,
            "alert_type": p.alert_type,
        })
    session.close()
    return templates.TemplateResponse(request, "index.html", {"products": result})

@app.post("/track")
def add_product(url: str = Form(...)):
    logger.info(f"Received request to track: {url}")
    try:
        track(url)
        return RedirectResponse(url="/", status_code=303)
    except ValueError as e:
        logger.error(f"Error tracking {url}: {e}")
        error_msg = str(e)
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)

@app.post("/delete")
def delete_product(product_id: int = Form(...)):
    session = SessionLocal()

    product = session.query(Product).filter_by(id=product_id).first()

    if product:
        session.delete(product)
        session.commit()
        logger.info(f"Deleted product id={product_id} ({product.title})")
    else:
        logger.warning(f"Delete requested for unknown product id={product_id}")
    session.close()
    return RedirectResponse(url="/", status_code=303)


@app.post("/set_alert")
def alert_product(product_id: int = Form(...), alert_type: str = Form("")):
    session = SessionLocal()
    product = session.get(Product, product_id)

    if product:
        product.alert_type = alert_type or None  # "" from the "Off" option -> None
        session.commit()
        logger.info(f"Set alert_type={alert_type or 'None'} for product id={product_id}")
    else:
        logger.warning(f"Set alert requested for unknown product id={product_id}")

    session.close()
    return RedirectResponse(url="/", status_code=303)
