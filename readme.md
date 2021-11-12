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
* Then add the script to Windows Task Scheduler(Windows), chron(Linux) or OSX Automator


# Supported sites

* [Komplett.no](https://www.komplett.no/)