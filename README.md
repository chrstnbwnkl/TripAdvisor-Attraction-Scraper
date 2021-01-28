# Tripscrape
A TripAdvisor attraction scraper for attractions and their reviews. Uses beautifulsoup most of the time and Selenium with headless Chrome only where necessary (namely for attractions details like coordinates and the number of pages of the reviews). Developed for retrieving all London attractions and their reviews, a more flexible CLI might follow. Working on macOS 10.15.7 as of Jan 2021.

# Requirements

* PostgreSQL
* Conda
* Chromium driver for Selenium

# Installation

````bash
git clone
cd tripscrape
open .env.template
````

Configure your postgres config params and save as .env

Set up your database:

````
psql <login credentials> < db_dump.sql
````

Install conda dependencies into new env (check the env name, default is "scrape"):
````
conda env create --file env.yaml
conda activate <new env name>
````

Finally, start the attraction scraper by running
````
python tripscrape/attractions.py
````
If that one ran successfully, run the review scraper in the same fashion, but make sure to check out the attraction types to be scraped before in `main()`

Enjoy!
