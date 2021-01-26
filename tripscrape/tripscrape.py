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
    db_conn : psycopg2.connection()
        a psycopg2 connection to PostgreSQL
    place_id : int
        a TripAdvisor place ID
    base_url : string
        The base url to be formatted
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
        soup : BeautifulSoup
            A BeautifulSoup instance of the webpage to be searched
        search_type: str
            Whether the webpage displays reviews or attraction search results (accepts "reviews" or "attractions")

        Returns
        -------
        int
            number of pages found
        """
        if search_type == "reviews":
            num_string = soup.find("span", {"class" : "mxlinKbW"}).get_text()
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
        search_type: str
            Whether the webpage displays reviews or attraction search results (accepts "reviews" or "attractions")

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
            pages =  [""] + ["-or{}-".format(i*5) for i in range(amount)][2133:]
            return [url.format(i) for i in pages]
    
    def update_record(self, querystring):
        """
        Executes the passed querystring

        Parameters
        ----------

        querystring : str
            A querystring to be executed in PostgreSQL
        """
        self.db_cur.execute(querystring)
        self.db_conn.commit()
        return

class Attraction:
    """
    TripAdvisor attraction class.

    Parameters
    ----------
    ID : int
        TripAdvisor attraction id
    name : str
        the attraction's full, human readable, name
    url : str
        the relative URL to the attraction's TripAdvisor page
    attr_type : str
        the attraction's type according to TripAdvisor's classification system
    location : list
        the coordinate pair in [Lat, Lon] of an attraction's location
    num_reviews : dict
        the number of reviews in the three most frequent review languages
    """

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
        self._ID = int(re.match(r"/Attraction_Review-g\d*-d(\d*)-", value).group(1)) # also sets value for ID using regex
    
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
    """
    Tripadvisor review class.

    Parameters
    ----------
    ID : int
        the TripAdvisor review id
    title : str
        the review title
    rating : int
        the review rating (between 1 and 5)
    date : str
        the date of the review in the format (month year), or (day month) if less than a month ago
    full : str
        the full text of the review
    attr_id : int
        TripAdvisor attraction id of the reviewed attraction
    user_profile : str
        the relative URL to the user profile
    """
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
    """
    TripAdvisor user class.

    Parameters
    ----------
    profile : str
        the relative URL to the user profile
    location : str
        the self-reported home location of a user
    contributions : int
        the number of contributions of a user on TripAdvisor
    helpful_votes : int
        the number of helpful votes a user has received on TripAdvisor
    """
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