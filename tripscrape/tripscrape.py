import argparse

parser = argparse.ArgumentParser(description='Scrape Tripadvisor attractions from a place, their reviews, and reviewer information.')
parser.add_argument('pid', metavar='PID', type=int,
                    help='a TripAdvisor place ID')
parser.add_argument('--type', type=str, metavar="type",
                    help='choose an attraction type. defaults to all')

args = parser.parse_args()
print(args.type)

BASEURL = "https://www.tripadvisor.com/"