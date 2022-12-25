# Price Tracker 

## Description: 

This repo is for tracking prices and stock for websites


# How to setup

* Download repo
* Run this command inn the folder
    ```bash
    python -m pip install -r requirements.txt
    ```
* Add the sites you want to check to the json file like this:
    ```json
    {
        "https://www.komplett.no/product/1139425/datautstyr/pc-komponenter/minnebrikker/gskill-trident-z-neo-ddr4-3600mhz-32gb": {
            "Name": "",
            "Price": "",
            "Stock": ""
        },
        "https://www.komplett.no/product/1180525/datautstyr/lagring/harddiskerssd/ssd-m2/patriot-viper-vp4100-2tb-m2-ssd?q=patriot%20viper%20vp4100": {
            "Name": "",
            "Price": "",
            "Stock": ""
        }
    }
    ``` 
* Go to the [PushBullet API key site](https://www.pushbullet.com/#settings) and press the Create Access Token button
* Copy the token
* Create a file called "pushbullet_api_key.txt" and paste your pushbullet api key inside 
* Download the pushbullet app on yor phone and sign in
* Then add the script to Windows Task Scheduler(Windows), chron(Linux) or OSX Automator, with your desired intervals


# Supported sites

* [Komplett.no](https://www.komplett.no/)
* [Multicom.no](https://www.multicom.no/)
* [Deal.no](https://deal.no/)
* [Prisguiden.no](https://prisguiden.no/)
    * [Search page](https://prisguiden.no/kategorier/tv?f[867][]=OLED&f[m][]=Philips&s=price%20asc) and specified [products](https://prisguiden.no/produkt/philips-55oled705-12-498120) 
    * Stock will be N/A on search pages since there is no stock information there 