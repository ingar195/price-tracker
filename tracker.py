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


def komplett(soup, url):
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


def Notify(Name, CurrentState):
    apiKey = ""
    with open("pushbullet_api_key.txt", "r") as f:
        apiKey = f.readline()
    pb = Pushbullet(apiKey)
    pb.push_note(Name, CurrentState)


def site(url, data):    
    if "komplett" in url:
        writeConfig(komplett(get(url), url), data)
    else:
        print(f"Not supported url {url}")
    

def writeConfig(returnFromStore, data):
    name = returnFromStore[0]
    stock = returnFromStore[1]
    price = returnFromStore[2]
    print(f"name: {name}, stock: {stock}, price: {price}")
    

def readConfig():
    with open("products.json") as jsonFile:
        return json.load(jsonFile)






data = readConfig()

for url in data:
    print(url)
    site(url, data[url])
