import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
import json


def get(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def getSpan(soup, attr, txt):
    return soup.find_all('span', attrs={attr: txt})


def stripper(string, bef, aft):
    return ((str(string[0]))[bef:aft])


def komplett(soup):
    # Get name
    name = stripper(getSpan(soup, "data-bind", "text: webtext1"), 33, -7)
    print(f"Name: {name}")

    # Get stock
    stock = stripper(getSpan(soup, "class", "stockstatus-stock-details"), 40, -22)
    print(f"Stock: {stock}")

    # Get price
    price = stripper(getSpan(soup, "class", "product-price-now"), 59, -9).replace(u'\xa0', u'')
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
