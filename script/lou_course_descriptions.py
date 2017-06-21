# This is a python script to populate the course descriptions from Lou's list

current_sem = "Fall 2017"
lou_url = "https://rabi.phys.virginia.edu/mySIS/CC2/Mathematics.html"

from bs4 import BeautifulSoup
import urllib2
import csv

html = urllib2.urlopen(lou_url).read()
soup = BeautifulSoup(html, "lxml")
table = soup.select("table")[1]

data = []

rows = table.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])

