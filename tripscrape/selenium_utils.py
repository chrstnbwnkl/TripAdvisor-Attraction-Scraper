from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re

def get_attr_details(url):
    """
    Opens a headless Chrome instance and parses attraction details for which web page rendering is necessary.

    Parameters
    ----------
    url : str
        the attraction's url
    
    Returns
    -------
    attraction details : tuple
        a tuple of (coordinates, number of reviews, number of pages)
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome("./chromedriver", options=chrome_options)

    driver.get(url)
    try:
        img = WebDriverWait(driver, 7)\
                .until(EC.presence_of_element_located((By.XPATH, ".//span[@data-test-target='staticMapSnapshot']/img")))\
                .get_attribute("src")
        location = re.match(r".*center=(\d{2}.\d*),(-{0,1}\d{1}.\d*)&", img)
        coords = [float(location.group(1)), float(location.group(2))]
    except:
        coords = [None, None]

    number_of_reviews = {}
    try:
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, './/ul[@class="_2lcHrbTn"]')))
        li = driver.find_elements_by_xpath('.//li[@class="ui_radio _3gEj_Jb5"]')
        for lan in li[1:]:
            v = lan.find_element_by_xpath('.//label[@class="bUKZfPPw"]').text
            match = re.match(r"(.*)\((\d*,*\d*)\)", v)
            number_of_reviews[match.group(1)] = int(match.group(2).replace(",",""))
    except:
        number_of_reviews = None


    try:
        num_pages = int(driver.find_elements_by_xpath('.//div[@class="pageNumbers"]//a[@class="pageNum "]')[-1].text)
    except:
        num_pages = 1

    driver.quit()
    return (coords, number_of_reviews, num_pages)