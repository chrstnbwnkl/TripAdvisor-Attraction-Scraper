from time import sleep
from requests import get
import re
from bs4 import BeautifulSoup as bs
import psycopg2 as db


class Scraper:
    """
    Base class for Tripadvisor scraper

    Parameters
    ----------
    base_url : string
        The base url to be formatted
    place_id : int
        A Tripadvisor place ID
    """

    def __init__(self, db_conn = None, place_id = 186338, base_url="https://www.tripadvisor.com"):
        self.db_conn = db_conn
        self.db_cur = db_conn.cursor()
        self.base_url = base_url
        self.place_id = place_id
    



    def get_num_pages(self, soup, search_type):
        """
        Gets the number of pages to parse.

        Parameters
        ----------
        url : str
            A URL to a page of results/reviews to retrieve the number of pages from
        el: str
            The element where the number of pages is located  

        Returns
        -------
        int
            number of pages found on url
        """
        if search_type == "reviews":
            num_string = soup.find("span", {"class" : "_1yuvE2vR"}).get_text()
            num_pages = int(num_string.replace(",", ""))
            return num_pages

        elif search_type == "attractions":
            num_string = soup.find('div', {'class': 'pageNumbers'}).findChildren(recursive=True)[-1].get_text()
            num_pages = int(num_string)
            return num_pages

        

    def generate_page_links(self, amount, search_type, url= None):
        """
        Generates links for every page of the search results or reviews.

        Parameters
        ----------
        url : str
            a URL to be formatted
        amount : int
            number of pages to be generated

        Returns
        -------
        list
            list of links to every page of search results/reviews
        """

        if search_type == "attractions":
            pages =  [""] + ["oa{}".format(i*30) for i in range(amount)][1:]
            return [self.base_url.format(self.place_id, i) for i in pages]

        elif search_type == "reviews":
            url = url.replace("-Reviews", "-Reviews-{}")
            pages =  [""] + ["-or{}-".format(i*5) for i in range(amount)][1:]
            return [url.format(i) for i in pages]
    
    def update_record(self, querystring):
        self.db_cur.execute(querystring)
        self.db_conn.commit()
        return

class Attraction:

    def __init__(self, ID = None, name = None, url = None, attr_type = None, location = None, num_reviews = 0):
        self._ID = ID
        self._name = name
        self._url = url
        self._attr_type = attr_type
        self._location = location
        self._num_reviews = num_reviews

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        self._ID = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
        self._ID = int(re.match(r"/Attraction_Review-g\d*-d(\d*)-", value).group(1))
    
    @property
    def attr_type(self):
        return self._attr_type

    @attr_type.setter
    def attr_type(self, value):
        self._attr_type = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value
    
    @property
    def num_reviews(self):
        return self._num_reviews

    @num_reviews.setter
    def num_reviews(self, value):
        self._num_reviews = value


class Review:

    def __init__(self, ID = None, title = None, rating = None, date = None, full = None, attr_ID = None, user_profile = None):
        self._ID = ID
        self._title = title
        self._rating = rating
        self._date = date
        self._full = full
        self._attr_ID = attr_ID
        self._user_profile = user_profile
    
    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        self._ID = value
    
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
    
    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value
    
    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
    
    @property
    def full(self):
        return self._full

    @full.setter
    def full(self, value):
        self._full = value

    @property
    def attr_ID(self):
        return self._attr_ID

    @attr_ID.setter
    def attr_ID(self, value):
        self._attr_ID = value
    
    @property
    def user_profile(self):
        return self._user_profile

    @user_profile.setter
    def user_profile(self, value):
        self._user_profile = value

class User:

    def __init__(self, profile = None, location = None, contributions = None, helpful_votes = None):
        self._profile = profile
        self._location = location
        self._contributions = contributions
        self._helpful_votes = helpful_votes

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value
    
    @property
    def contributions(self):
        return self._contributions

    @contributions.setter
    def contributions(self, value):
        self._contributions = value

    @property
    def helpful_votes(self):
        return self._helpful_votes

    @helpful_votes.setter
    def helpful_votes(self, value):
        self._helpful_votes = value