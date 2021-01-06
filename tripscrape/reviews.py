import argparse
import logging
import json
import re
from os.path import isfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
import selenium


parser = argparse.ArgumentParser(description='Scrape Tripadvisor reviews from a list of attractions provided by the attractions scraper. Retrieves full review, rating, user ID, date, as well as lat/lon of the attraction.')
parser.add_argument('--pid', type=int, help='a TripAdvisor place ID', default=186338)
args = parser.parse_args()

logging.basicConfig(filename='reviews.log', level=logging.INFO, filemode="w", format='%(asctime)s:%(message)s')
logger = logging.getLogger(__name__)


with open("url_list_{}.json".format(args.pid), "r") as f:
    attractions = json.loads(f.read())

BASEURL = "https://www.tripadvisor.com"
LANGUAGE = "?filterLang=EN"

driver = webdriver.Chrome("./tripscrape/chromedriver")

def get_substring(string, substring, mode="after"):
    """
    Removes a substring from the beginning or end of a provided string.

    Parameters
    ----------
    string : str
        string that will be searched
    
    substring : str
        string that will be removed from the string

    mode : str
        toggles whether the part of the string before or after the substring will be returned. Defaults to after.

    Returns
    -------
    str
        the original string up until or after the substring        
    """
    index = string.index(substring)
    end_index = index + len(substring)
    return string[end_index:] if mode=="after" else string[:index] if mode=="before" else string

def wait_for_review_elements(xpath):
    """
    Waits for the appearance of a list of elements.

    Parameters
    ----------
    xpath : list
        list of xpaths to locate the element

    Returns
    -------
    True
    """
    for i in xpath:
        WebDriverWait(driver, 3)\
            .until(EC.presence_of_element_located((By.XPATH, i)))

    return True

def click_accept(s):
    """
    Awaits the appearance of the button element for s seconds, and clicks accept as soon as it appears in the DOM.

    Parameters
    ----------
    s : int
        max number of seconds to wait for the button to be clickable
    """
    WebDriverWait(driver, s)\
                    .until(EC.element_to_be_clickable((By.XPATH, ".//button[@class='evidon-banner-acceptbutton']")))\
                    .click()

def get_latlon(s):
    """
    Retrieves lat/lon information from the current attraction and stores it in the review dictionary.

    Parameters
    ----------
    s : int
        max number of seconds to wait for the button to be clickable
    
    Returns
    -------

    list
        a list in the format [lat, lon]
    """
    img = WebDriverWait(driver, s)\
                .until(EC.presence_of_element_located((By.XPATH, ".//span[@data-test-target='staticMapSnapshot']/img")))\
                .get_attribute("src")
    location = re.match(r".*center=(\d{2}.\d*),(-{0,1}\d{1}.\d*)&", img)
    return [float(location.group(1)), float(location.group(2))]

def get_numer_of_reviews(s):
    """
    Retrieves the number of reviews of a given attraction.

    Parameters
    ----------
    s : int
        max number of seconds to wait for the button to be clickable

    Returns
    -------
    int
        number of reviews of a given attraction
    """
    n = WebDriverWait(driver, s).until(EC.presence_of_element_located((By.XPATH, './/span[@class="_1yuvE2vR"]'))).text
    m = int(n.replace(",", ""))
    return m


def get_review_contents(attraction):
    """
    Gets the contents of each review

    Retrieves the number of review pages on a given attraction page, and for every page:
     - expands the expandable reviews, 
     - locates the review container, and for every review in the container:
         - retrieves the title, rating, date, full review and user URL.
    
    Returns
    -------
    list
        list with review objects 

    """

    try:
        num_pages = driver.find_elements_by_xpath('.//div[@class="pageNumbers"]//a[@class="pageNum "]')[-1].text
    except:
        num_pages = 1
    
    reviews = list()

    # 2nd level (review pages)
    for i in range(0, int(num_pages)):
        # click to expand all reviews
        sleep(2)
        try:
            expand = driver.find_element_by_xpath("//span[@class='_3maEfNCR']")
            driver.execute_script("arguments[0].click();", expand)
        except (ElementClickInterceptedException, NoSuchElementException):
            logger.info("Comments not expandable on page {} at attraction {}.".format(i+1, attractions[attraction]["name"]))
        
        try:
            WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, './/div[@data-test-target="reviews-tab"]')))
            review_divs = driver.find_elements_by_xpath('.//div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')
        except:
            logger.info("No reviews located at attraction {}".format(attractions[attraction]["name"]))

        # 3rd level (reviews)
        for r_i, r in enumerate(review_divs):
            review = {}
            wait_for_review_elements(['.//div[@class="glasR4aX"]', 
                                    ".//span[contains(@class, 'ui_bubble_rating bubble_')]",
                                    './/span[@class="_34Xs-BQm"]',
                                    './/div[@class="cPQsENeY"]',
                                    './/a[@class="_3x5_awTA ui_social_avatar inline"]',
                                    './/span[@class="default _3J15flPT small"]',
                                    './/span[@class="_1fk70GUn"]'
                                    ])
            #review['title'] = wait_for_review_element('.//div[@class="glasR4aX"]').text
            review['title'] = r.find_element_by_xpath('.//div[@class="glasR4aX"]').text
            review['rating'] = int(r.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3][0])
            full_date = r.find_element_by_xpath('.//span[@class="_34Xs-BQm"]').text
            review['date'] = get_substring(full_date, "Date of experience: ")
            review['full'] = r.find_element_by_xpath('.//div[@class="cPQsENeY"]').text
            try:
                profile_link = r.find_element_by_xpath('.//a[@class="_3x5_awTA ui_social_avatar inline"]').get_attribute("href")
                review['user_profile'] = get_substring(profile_link, BASEURL)
            except:
                logger.info("No user profile at attraction {}, page {}, review {}".format(attractions[attraction]["name"], i+1, r_i+1))

            try:
                review['user_location'] = r.find_element_by_xpath('.//span[@class="default _3J15flPT small"]').text
            except:
                logger.info("No user location at attraction {}, page {}, review {}".format(attractions[attraction]["name"], i+1, r_i+1))
            
            try:
                review['user_contributions'] = int(r.find_element_by_xpath('.//span[@class="_1fk70GUn"]').text.replace(",",""))
            except:
                logger.info("No user contributions at attraction {}, page {}, review {}".format(attractions[attraction]["name"], i+1, r_i+1))

            
            reviews.append(review)

        # change page
        try:
            driver.find_element_by_xpath('.//a[@class="ui_button nav next primary "]').click()
        except:
            logger.info("Next button not clickable at attraction {}, page {}".format(attractions[attraction]["name"], i+1))

    return reviews
            


        


def do_scrape():
    # 1st level (attractions)
    for i, idx in enumerate([900]):
        if not isfile("reviews/reviews_{}_{}.json".format(args.pid,idx)):
            logger.info("Scraping attraction: " + attractions[idx]["name"])
            url = "{}{}{}".format(BASEURL, attractions[idx]["url"], LANGUAGE)
            driver.get(url)
            if i == 0:
                click_accept(10)

            try:
                attractions[idx]["coordinates"] = get_latlon(5) 
            except:
                logger.warning("Could not fetch coordinates at attraction {}".format(attractions[idx]))
            
            try:
                attractions[idx]["num_reviews"] = get_numer_of_reviews(5)
            except Exception as e:
                attractions[idx]["num_reviews"] = 0
                logger.warning("No reviews at attraction {}. {}".format(attractions[idx]["name"], str(e)))

            if attractions[idx]["num_reviews"] != 0:
                reviews = get_review_contents(idx)
                attractions[idx]["reviews"] = reviews
            with open("reviews/reviews_{}_{}.json".format(args.pid,idx), "w") as f:
                json.dump(attractions[idx], f)
        else:
            logger.warning("reviews/reviews_{}_{}.json already exists!".format(args.pid,idx))




def main():
    logger.info("Start scraping reviews...")
    do_scrape()
    driver.close()
    logger.info("Scrape done, stopping...")

if __name__ == "__main__":
    main()