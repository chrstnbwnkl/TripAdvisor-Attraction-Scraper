# Tripscrape
A TripAdvisor attraction scraper.

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
