from time import sleep
import json
import re
from dotenv import dotenv_values
from random import random
from requests import get
import psycopg2 as db
import selenium_utils
from bs4 import BeautifulSoup as bs
from tripscrape import Scraper, Attraction, Review, User


class ReviewScraper(Scraper):
    def __init__(
                self, 
                db_conn = None, 
                place_id = 186338, 
                base_url="https://www.tripadvisor.com", 
                search_type = "reviews",
                attr_types = ("Sights & Landmarks")
                ):
        super().__init__(db_conn, place_id, base_url)
        self.search_type = search_type
        self._attr_types = attr_types
    
    @property
    def attr_types(self):
        return self._attr_types

    @attr_types.setter
    def attr_types(self, value):
        self._attr_types = value

    def get_num_pages(self, soup):
        return super().get_num_pages(soup, search_type=self.search_type)
    
    def generate_page_links(self, url, amount):
        return super().generate_page_links(amount=amount, search_type=self.search_type, url=url)
    
    def read_attractions(self):
        """
        Read attractions from the attractions table in the database.

        Returns
        -------
        list
            a list of dictionaries
        """
        query_template = 'SELECT id, url FROM attractions'

        if self.attr_types == "all":
            return self.db_cur.execute(query_template)
        elif len(self.attr_types) == 1:
            query_template += ' WHERE attr_type IN (%s) LIMIT 2'
            return self.db_cur.execute(query_template, (self.attr_types,))
        elif len(self.attr_types) > 1:
            query_template += ' WHERE attr_type IN %s LIMIT 2'
            return self.db_cur.execute(query_template, (self.attr_types,))
    
    def update_attraction(self, attr):
        querystring = self.db_cur.mogrify("""UPDATE attractions SET geom = ST_SetSRID(ST_MakePoint(%s, %s),4326), num_reviews = %s WHERE id = %s;""", (attr.location[1], attr.location[0], json.dumps(attr.num_reviews), attr.ID))

        return super().update_record(querystring)
    
    def update_review(self, review):
        querystring = self.db_cur.mogrify(
                            """INSERT INTO reviews (ID, title, rating, date, "full", attr_ID, user_profile) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""", tuple(review.__dict__.values())
                        )
        return super().update_record(querystring)
    
    def update_user(self, user):
        print("Updating user {}".format(user.profile))
        querystring = self.db_cur.mogrify(
                            """INSERT INTO users (profile, location, contributions, helpful_votes) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""", tuple(user.__dict__.values())
                        )
        return super().update_record(querystring)

    def get_attr_details(self, url):
        return selenium_utils.get_attr_details(url)
    
    def print_missing_info(self, info_type, attr_ID, page_no, review_no, url):
        print("No {} found at attraction {}, page {}, review {}.\nURL: {}".format(info_type, attr_ID, page_no + 1, review_no + 1, url))

    def scrape_page(self, url, attr_ID, index):
        print("Scraping page {}".format(url))
        soup = bs(get(url).content, "html.parser")
        review_divs = soup.find_all("div", {"class" : "Dq9MAugU T870kzTX LnVzGwUB"})

        for ridx, div in enumerate(review_divs):
            review = Review()
            user = User()

            review.ID = div.find("div", {"class" : "oETBfkHU"}).get("data-reviewid")
            review.title = div.find("div", {"class" : "glasR4aX"}).get_text()
            review.rating = int(div.find('span', {"class" : "ui_bubble_rating"}).get("class")[1].split("_")[1][0])
            review.full = div.find("div", {"class" : "cPQsENeY"}).get_text().replace("…", "")
            review.attr_ID = attr_ID
            try:
                raw_date = div.find("div", {"class" : "_2fxQ4TOx"}).get_text()
                review.date = re.match(r".*wrote a review (.*)", raw_date).group(1)
            except AttributeError:
                self.print_missing_info("date", attr_ID, index + 1, ridx + 1, url)

            try:
                review.user_profile = div.find("a", {"class" : "_3x5_awTA ui_social_avatar inline"}).get("href")
                user.profile = review.user_profile
            except AttributeError:
                self.print_missing_info("user profile", attr_ID, index + 1, ridx + 1, url)
            
            try:
                user.location = div.find("span", {"class" : "default _3J15flPT small"}).get_text()
            except AttributeError:
                self.print_missing_info("user location", attr_ID, index + 1, ridx + 1, url)
                user.location = [None, None]
            
            try:
                user.contributions = int(div.find_all("span", {"class" : "_1fk70GUn"})[0].get_text().replace(",", ""))
            except:
                self.print_missing_info("user contributions", attr_ID, index + 1, ridx + 1, url)
            
            try:
                user.helpful_votes = int(div.find_all("span", {"class" : "_1fk70GUn"})[1].get_text().replace(",", ""))
            except:
                self.print_missing_info("helpful votes", attr_ID, index + 1, ridx + 1, url)
            
            self.update_user(user)
            self.update_review(review)

        return

    def do_scrape(self):
        self.read_attractions()
        while True:
            row = self.db_cur.fetchone()

            if row == None:
                break
            
            current_url = self.base_url + row[1]
            a = Attraction(row[0])
            a.location, a.num_reviews = self.get_attr_details(current_url)
            print(a.location, a.num_reviews)
            self.update_attraction(a)
            
            entry_soup = bs(get(current_url).content, "html.parser")
            number_of_pages = self.get_num_pages(entry_soup)
            links = self.generate_page_links(current_url, number_of_pages)

            for index, link in enumerate(links):
                self.scrape_page(link, a.ID, index)
                sleep(1.3 + random())

def main():
    conn = db.connect(**dotenv_values())
    r = ReviewScraper(db_conn=conn, attr_types=('Other',))
    r.do_scrape()
    r.db_conn.close()

if __name__ == "__main__":
    main()