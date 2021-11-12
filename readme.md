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
* Go to [this site](https://www.pushbullet.com/#settings) and press the Create Access Token button
* Copy the token
* Create a file called "pushbullet_api_key.txt" and paste your pushbullet api key inside 
* Download the pushbullet app on yor phone and sign in
* Then add the script to Windows Task Scheduler(Windows), chron(Linux) or OSX Automator, with your desired intervals


# Supported sites

* [Komplett.no](https://www.komplett.no/)