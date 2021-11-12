import requests
from bs4 import BeautifulSoup


def get(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def getSpan(soup, attr, txt):
    return soup.find_all('span', attrs={attr: txt})


def komplett(soup, url):
    # Get stock
    stock = getSpan(soup, "class", "stockstatus-stock-details")
    # Strip stock
    stock = (str(stock[0]))[40:-22]
    print(f"Stock: {stock}")
    
    # Get price
    price = getSpan(soup, "class", "product-price-now")
    # Strip price
    price = str(price[0])[59:-9]
    price = price.replace(u'\xa0', u'')
    print(f"Price: {price}")

    return price, stock


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
