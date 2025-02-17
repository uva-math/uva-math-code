# July 2020 update
# Lou's list has moved and has changed format. Therefore I am removing course descriptions from the website and will refer to Lou's List

############################################################################################################

# This is a python script to populate the course descriptions from Lou's list
# Usage:
# python lou_course_descriptions.py  > ../_data/courses.yml
# (requires installing bs4 and lxml)
# DO NOT FORGET TO UPDATE THE CURRENT SEMESTER for the script to work properly

current_semester = "Fall 2020"
lou_url = "https://louslist.org/CC/Mathematics.html"

from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import csv

# html = urllib.request.urlopen(lou_url).read()
f = open("page.html", "r")
html = f.read()
soup = BeautifulSoup(html, "lxml")
table = soup.select("table")[1]

data = []

rows = table.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])

print("# List of all courses, generated by the Python script scripts/lou_course_descriptions.py")
print("# all fields are self-explanatory; if the course is graduate this should be indicated")
print("")
print("# There is a list of courses that will not be shown, in file masked_courses.yml")
print("")
print("# There is a number of courses which must be added manually because they are not in Lou's list.")
print("# They are in courses_added_manually.yml")
print("")
print("# Some courses are renamed, hardcoded in the script")
print("")


for i in range(2, len(data)):    
    print(data[i])
    if i%2 :
        print("- name: \"", data[i][1], "\"")
        print("  number:", data[i][0].replace("MATH ", "", 1))
        if int( data[i][0].replace("MATH ", "", 1) ) >= 5000 :
            print("  graduate: true")
    else :
        if data[i][0] == "Offered" + current_semester :
            print("  offered: " + current_semester)
            print("  descr: \"", data[i][1].split("Course was offered", 1)[0], "\"")
        else:
            print("  descr: \"", data[i][0].split("Course was offered", 1)[0], "\"")
        print("")
