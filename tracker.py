import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet


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
    price = stripper(getSpan(soup, "class", "product-price-now"), 59, -9)
    price = price.replace(u'\xa0', u'')
    print(f"Price: {price}")

    Notify("Update", (f"Stock: {stock}\nPrice: {price}"))
    return price, stock


def Notify(Name, CurrentState):
    apiKey = ""
    with open("pushbullet_api_key.txt", "r") as f:
        apiKey = f.readline()
    pb = Pushbullet(apiKey)
    pb.push_note(Name, CurrentState)


def site(url):
    if "komplett" in url:
        komplett(get(url), url)
    else:
        print(f"Not supported url {url}")


fileName = "products.txt"
with open(fileName, "r") as f:
    for url in f.readlines():
        print(f"URL: {url}")
        site(url)
