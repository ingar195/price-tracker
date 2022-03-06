import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
import json
import logging
import os


def get(url):
    logging.debug("Get")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def norChars(var):
    logging.debug("norChars({var})")

    var = var.replace("\u00e5", "a")
    logging.debug(var)
    return var


def getSpan(soup, types, attr, txt):
    logging.debug(f"soup, {types}, {attr}, {txt}")

    if attr or txt != None:
        logging.debug("attr or txt != None")
        for item in soup.find_all(types, attrs={attr: txt}):
            stripped = norChars(item.text.strip('\r\n\t,-stkNå+').replace(u'\xa0', u''))
            # logging.debug(stripped)
            return stripped


def komplett(soup):
    logging.debug("komplett(soup)")

    # Get name
    name = getSpan(soup, "span", "data-bind", "text: webtext1")
    logging.info(f"Name: {name}")

    # Get stock
    stock = int(getSpan(soup, "span", "class", "stockstatus-stock-details").strip(" stk. på lager").replace("+", ""))
    logging.info(f"Stock: {stock}")

    # Get price
    price = int(getSpan(soup, "span", "class", "product-price-now"))
    logging.info(f"Price: {price}")

    logging.debug(name, price, stock)
    return name, price, stock


def multicom(soup):
    logging.debug("multicom(soup)")

    # Get name
    name = getSpan(soup, "span", "class", "_brand_name")
    name += " " + getSpan(soup, "span", "class", "b-product-name__extra")
    logging.info(f"Name: {name}")

    # Get stock
    stock = int(getSpan(soup, "span", "class", "b-stock-info__amount"))
    logging.info(f"Stock: {stock}")

    # Get price
    price = int(getSpan(soup, "span", "class", "b-product-price_"))
    logging.info(f"Price: {price}")

    logging.debug(name, price, stock)
    return name, price, stock


def deal(soup):
    logging.debug("deal(soup)")

    # Get name
    name = getSpan(soup, "h2", "class", "partname")
    logging.info(f"Name: {name}")

    # Get stock
    stock = int(str(getSpan(soup, "span", "class", "b-show-stock__quantity")))
    logging.info(f"Stock: {stock}")

    # Get price
    price = int(getSpan(soup, "span", "class", "pricedetails relative"))
    logging.info(f"Price: {price}")

    logging.debug(name, price, stock)
    return name, price, stock


def prisguiden(soup):
    logging.debug("prisguiden(soup)")

    # Get name
    name = getSpan(soup, "span", "class", "product-shortname")
    logging.info(f"Name: {name}")

    # Get stock
    stock = str(getSpan(soup, "span", "class", "quote"))
    logging.info(f"Stock: {stock}")

    price = int(getSpan(soup, "a", "class", "button-to-shop number").strip("RekordbilligTilbud stk. pa lager"))
    logging.info(f"Price: {price}")

    logging.debug(name, price, stock)
    return name, price, stock


def farmasiet(soup):
    logging.debug("Farmasiet")

    # Get name
    name = getSpan(soup, "span", "class", "Product__Brand")
    logging.info(f"Name: {name}")

    # Get stock
    try:
        stock = str(getSpan(soup, "span", "class", "Product__Availability")).lstrip(" ").rstrip(" ")
        logging.info(f"Stock: {stock}")
    except:
        stock = str(getSpan(soup, "span", "class", "Product__Availability Product__Availability--NotInStock")).lstrip(" ").rstrip(" ")
        logging.info(f"Stock: {stock}")

    price = int(getSpan(soup, "span", "class", "Product__PriceDefault"))
    logging.info(f"Price: {price}")

    logging.debug(name, price, stock)
    return name, price, stock


def apotekfordeg(soup):
    logging.debug("apotekfordeg")

    # Get name
    name = getSpan(soup, "span", "class", "product_title entry-title")
    logging.info(f"Name: {name}")

    # Get stock
    price = str(getSpan(soup, "span", "class", "regular-price-text")).strip("\r\n").lstrip(" ").rstrip(" ")
    logging.info(f"Stock: {price}")
    try:
        stock = str(getSpan(soup, "p", "class", "stock in-stock"))
        logging.info(f"Price: {stock}")
    except:
        stock = str(getSpan(soup, "p", "class", "stock out-of-stock"))
        logging.info(f"Price: {stock}")

    logging.debug(name, price, stock)
    return name, price, stock     


def Notify(alert):
    logging.debug(f"Notify({alert})")
    apiKey = ""
    with open("pushbullet_api_key.txt", "r") as f:
        apiKey = f.readline().rstrip()
    pb = Pushbullet(apiKey)
    if len(alert) != 1:
        cnt = 0
        for al in alert:
            if cnt != 0:
                logging.info(f"Allert {al}")
                pb.push_note(alert[0], al)
            cnt += 1


def site(url, data):
    logging.debug(f"site({url}, {data})")
    if "komplett" in url:
        logging.debug("komplett")
        writeConfig(komplett(get(url)), data, url)

    elif "multicom" in url:
        logging.debug("multicom")
        writeConfig(multicom(get(url)), data, url)

    elif "deal" in url:
        logging.debug("deal")
        writeConfig(deal(get(url)), data, url)

    elif "prisguiden" in url:
        logging.debug("deal")
        writeConfig(prisguiden(get(url)), data, url)

    elif "farmasiet" in url:
        logging.debug("farmasiet")
        writeConfig(farmasiet(get(url)), data, url)

    elif "apotekfordeg" in url:
        logging.debug("apotekfordeg")
        writeConfig(apotekfordeg(get(url)), data, url)

    else:
        logging.error(f"Not supported url {url}")


def writeConfig(returnFromStore, data, url):
    logging.debug(f"writeConfig({returnFromStore}, {data}, {url})")
    name = returnFromStore[0]
    price = returnFromStore[1]
    stock = returnFromStore[2]
    logging.info(f"name: {name}, stock: {stock}, price: {price}")
    alert = [name]
    if data[url]["Name"] == "":
        data[url]["Name"] = name
        data[url]["Price"] = price
        data[url]["Stock"] = stock

    else:
        if data[url]["Price"] != price:
            alert.append("Price changed from {} to {}".format(name, data[url]["Price"], price))
            data[url]["Price"] = price

        if data[url]["Stock"] != stock:
            alert.append("Stock changed from {} to {}".format(data[url]["Stock"], stock))
            data[url]["Stock"] = stock

        if data[url]["Name"] != name:
            data[url]["Name"] = name

    with open(jsonFile, "w+") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))

    Notify(alert)


def readConfig():
    logging.debug("readConfig()")
    with open(jsonFile, "r") as jf:
        return json.load(jf)


input()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("Tracker.log"),
        logging.StreamHandler()
    ])

logger = logging.getLogger('my_app')

os.chdir(os.path.dirname(__file__)) 

jsonFile = "products.json"
data = readConfig()

for url in data:
    logging.info(f"Checking: {url}")
    site(url, data)
