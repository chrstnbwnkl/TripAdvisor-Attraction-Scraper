import logging
from time import sleep
import re
from random import random
import logging
from dotenv import dotenv_values
from requests import get
from bs4 import BeautifulSoup as bs
import psycopg2 as db
from tripscrape import Scraper, Attraction


class AttractionScraper(Scraper):
    """
    A scraper of attractions (extends the Scraper base class)

    Attributes
    ----------

    db_conn : psycopg2.connection()
        a psycopg2 connection to PostgreSQL
    place_id : int
        a TripAdvisor place ID
    base_url : string
        The base url to be formatted
    search_type : str
        the search type of the scraper (defaults to "reviews")
    """

    def __init__(
        self,
        db_conn=None,
        place_id=186338,
        base_url="https://www.tripadvisor.com/Attractions-g{}-Activities-{}-a_allAttractions.true",
        search_type="attractions",
    ):
        super().__init__(db_conn, place_id, base_url)
        self.search_type = search_type

    def get_num_pages(self, soup):
        return super().get_num_pages(soup, search_type=self.search_type)

    def generate_page_links(self, amount, url=None):
        return super().generate_page_links(
            amount=amount, search_type=self.search_type, url=url
        )

    def scrape_page(self, url):
        divs = bs(get(url).content, "html.parser").find_all(
            "div", {"class": "_25PvF8uO _2X44Y8hm"}
        )

        for div in divs:
            attraction = Attraction()
            attraction.url = (
                div.find("div", {"class": "_2pZeTjmb"}).find("a").get("href")
            )
            attraction.name = div.find("a", {"class": "_1QKQOve4"}).get_text()
            attraction.attr_type = div.find("span", {"class": "_21qUqkJx"}).get_text()
            self.update_attraction(attraction)

    def update_attraction(self, attr):
        """
        Checks whether the attraction exists in the database, updates if exists and inserts if not.

        Parameters
        ----------
        attraction : Attracion
            an Attraction instance
        """

        query_template = "INSERT INTO attractions (id, name, url, attr_type) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;"
        querystring = self.db_cur.mogrify(
            query_template, (attr.ID, attr.name, attr.url, attr.attr_type)
        )
        return super().update_record(querystring)

    def do_scrape(self):
        entry_page = self.base_url.format(self.place_id, "")
        entry_soup = bs(get(entry_page).content, "html.parser")
        number_of_pages = self.get_num_pages(entry_soup)
        links = self.generate_page_links(number_of_pages)

        for link in links:
            self.scrape_page(link)
            sleep(1.3 + random())


def main():
    conn = db.connect(**dotenv_values())
    a = AttractionScraper(db_conn=conn)
    a.do_scrape()
    a.db_conn.close()


if __name__ == "__main__":
    main()