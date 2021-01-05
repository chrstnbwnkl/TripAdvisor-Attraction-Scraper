import argparse
import json
from selenium import webdriver
import selenium


parser = argparse.ArgumentParser(description='Scrape Tripadvisor reviews from a list of attractions provided by the attractions scraper. Retrieves full review, rating, user ID, date, as well as lat/lon of the attraction.')
parser.add_argument('--pid', type=int, help='a TripAdvisor place ID', default=186338)

args = parser.parse_args()

with open("./url_list_{}.json".format(args.pid), "r") as f:
    attractions = json.loads(f.read())

