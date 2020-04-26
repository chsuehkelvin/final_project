from bs4 import BeautifulSoup
import http
import sqlite3
import json
import requests
import re
import csv

ranking = list(range(1,101))
cities_list = []
population_list = []
num = 0
base_url = "https://www.michigan-demographics.com/cities_by_population?fbclid=IwAR2w55mT2zrVc1I88YllXs75WpNKKubXsULivU1_W-otNKWLURv9TIeTWyE"
r = requests.get(base_url)
soup = BeautifulSoup(r.text, "html.parser")
cities = soup.find_all('a')[7:107]
for cities in soup.find_all('a')[7:107]:
    cities_list.append(cities.text)
population = soup.find_all(text = re.compile("(\d{1,3},\d\d\d)"))
population_list = [y.strip('\n ') for y in population]

conn = sqlite3.connect('michigan_data.sqlite')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS Michigan_Population")
cur.execute("CREATE TABLE Michigan_Population (ranking INTEGER PRIMARY KEY, city_name TEXT, population INTEGER)")
size = cur.execute("SELECT COUNT(city_name) FROM Michigan_Population")
count = 0
while count <= 20:
    cur.execute("SELECT COUNT(*) FROM Michigan_Population")
    before = cur.fetchone()[0]
    cur.execute("INSERT OR IGNORE INTO Michigan_Population (ranking, city_name, population) \
           VALUES (?,?,?)",(ranking[count], cities_list[count], population_list[count]))
    cur.execute("SELECT COUNT(*) FROM Michigan_Population")
    after = cur.fetchone()[0]
    count = count + after - before
# Save (commit) the changes

conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
