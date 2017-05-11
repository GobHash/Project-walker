"""
main module for this project
"""
import GtScraper as walker
import time


start = time.time()
walker.scrape_month(2016, '08')

print('It took {0:0.1f} seconds'.format(time.time() - start))