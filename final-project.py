import sqlite3
import json
import requests
from bs4 import BeautifulSoup
import http
import re
import csv

def get_resturants_info(data):
    tup = []
    resturant_list = data.get("businesses")
    if resturant_list != None:
        for resturant in resturant_list:
            name = resturant.get("name")
            rating = resturant.get("rating")
            price = resturant.get("price", None)
            if price == None:
                price = 0
            else:
                price = len(price)
            city = resturant.get("location").get("city")
            tup.append((name, rating, price, city))
    return tup

def get_yelp_data(location):
    api_key = "xksk-lRl1bTl6w5_kpeLidwN1knl2yhjCkF93CcsoHNMCH943MYIBtZgRZ4D1oPnzHr8wVaBa4sEoAjGnIJr7eSTP2wQydDHeXKoHznEcildc3dA6kC42sPB8OmaXnYx"
    search = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'bearer %s' %api_key}
    parameters = {'term':'resturant', 'limit':20, 'radius':9000, 'location':location}

    resturants = requests.get(url=search, params=parameters, headers=headers)
    data = resturants.json() 
    resturants_info = get_resturants_info(data)
    conn = sqlite3.connect('resturants.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Resturants (name TEXT UNIQUE PRIMARY KEY, city TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Metrics (name TEXT UNIQUE PRIMARY KEY, rating REAL, price INTEGER)''')
    for info in resturants_info:
        cur.execute('''INSERT OR IGNORE INTO Resturants VALUES (?, ?)''', (info[0], info[3]))  
        cur.execute('''INSERT OR IGNORE INTO Metrics VALUES (?, ?, ?)''', (info[0], info[1], info[2]))
    conn.commit()
    
    for row in cur.execute('SELECT * FROM Metrics'):
        print(row)
    print()
    for row in cur.execute('SELECT * FROM Resturants'):
        print(row)

    conn.close()

def get_list_cities_population(start):
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

    cur.execute("CREATE TABLE IF NOT EXISTS Michigan_Population (ranking INTEGER PRIMARY KEY, city_name TEXT, population INTEGER)")
    size = cur.execute("SELECT COUNT(city_name) FROM Michigan_Population")
    start = min(start, len(ranking) - 1)
    end = min(start + 20, len(ranking))
    for i in range(start, end):
        cur.execute("INSERT OR IGNORE INTO Michigan_Population (ranking, city_name, population) \
            VALUES (?,?,?)",(ranking[i], cities_list[i], population_list[i]))
            
    # Save (commit) the changes
    conn.commit()

    for row in cur.execute('SELECT * FROM Michigan_Population'):
        print(row)

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
    return cities_list

def main():
    answer = input("Would you like to collect data for: \n1 Restuarants\n2 Population\n::")
    if answer == '1':
        location = input("Enter a city:: ")
        get_yelp_data(location)
    elif answer == '2':
        start = int(input("Enter the XX largest city in Michigan (i.e. 1 or 12):: "))
        if start <= 0:
            start = 1
        cities = get_list_cities_population(start - 1)

main()