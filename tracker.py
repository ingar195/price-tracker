import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
import json


def get(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def getSpan(soup, types, attr, txt):
    if attr or txt != None:
        for item in soup.find_all(types, attrs={attr: txt}):
            return item.text.strip('\r\n\t,-stkNå').replace(u'\xa0', u'')
    elif attr or txt == None:
        return soup.find_all(types)


def komplett(soup):
    # Get name
    name = getSpan(soup, "span", "data-bind", "text: webtext1")
    print(f"Name: {name}")

    # Get stock
    stock = int(getSpan(soup, "span", "class", "stockstatus-stock-details").strip(" stk. på lager"))
    print(f"Stock: {stock}")

    # Get price
    price = int(getSpan(soup, "span", "class", "product-price-now"))
    print(f"Price: {price}")

    return name, price, stock


def multicom(soup):
    # Get name
    name = getSpan(soup, "span", "class", "_brand_name")
    name += " " + getSpan(soup, "span", "class", "b-product-name__extra")
    print(f"Name: {name}")

    # Get stock
    stock = int(getSpan(soup, "span", "class", "b-stock-info__amount"))
    print(f"Stock: {stock}")

    # Get price
    price = int(getSpan(soup, "span", "class", "b-product-price_"))
    print(f"Price: {price}")

    return name, price, stock


def deal(soup):
    # Get name
    name = getSpan(soup, "h2", "class", "partname")
    print(f"Name: {name}")

    # Get stock
    stock = int(str(getSpan(soup, "span", "class", "b-show-stock__quantity")))
    print(f"Stock: {stock}")

    # Get price
    price = int(getSpan(soup, "span", "class", "pricedetails relative"))
    print(f"Price: {price}")

    return name, price, stock


def Notify(alert):
    apiKey = ""
    with open("pushbullet_api_key.txt", "r") as f:
        apiKey = f.readline()
    pb = Pushbullet(apiKey)
    if len(alert) != 1:
        cnt = 0
        for al in alert:
            if cnt != 0:
                print(f"Allert {al}")
                pb.push_note(alert[0], al)
            cnt += 1


def site(url, data):
    if "komplett" in url:
        writeConfig(komplett(get(url)), data, url)
    elif "multicom" in url:
        writeConfig(multicom(get(url)), data, url)
    elif "deal" in url:
        writeConfig(deal(get(url)), data, url)
    else:
        print(f"Not supported url {url}")


def writeConfig(returnFromStore, data, url):
    name = returnFromStore[0]
    price = returnFromStore[1]
    stock = returnFromStore[2]
    print(f"name: {name}, stock: {stock}, price: {price}")
    alert = [name]
    if data[url]["Name"] == "":
        data[url]["Name"] = name
        data[url]["Price"] = price
        data[url]["Stock"] = stock

    else:
        if data[url]["Price"] != price:
            alert.append("Price changed from {} to {}".format(data[url]["Price"], price))
            data[url]["Price"] = price

        if data[url]["Stock"] != stock:
            alert.append("Stock changed from {} to {}".format(data[url]["Stock"], stock))
            data[url]["Stock"] = stock

    with open(jsonFile, "w+") as f:
        f.write(json.dumps(data))

    Notify(alert)


def readConfig():
    with open(jsonFile, "r") as jf:
        return json.load(jf)


jsonFile = "products.json"
data = readConfig()

for url in data:
    print(url)
    site(url, data)
