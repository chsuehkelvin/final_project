import sqlite3
import csv
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def make_join():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Yelp_Data (name TEXT UNIQUE PRIMARY KEY, rating REAL, price INTEGER, city TEXT)''')
    cur.execute('''INSERT OR IGNORE INTO Yelp_Data SELECT * FROM Metrics JOIN Resturants USING (name)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS All_Data (name TEXT UNIQUE PRIMARY KEY, rating REAL, price INTEGER, city TEXT, population INTEGER)''')
    cur.execute('''INSERT OR IGNORE INTO All_Data 
                    SELECT Yelp_Data.name, Yelp_Data.rating, Yelp_Data.price, Yelp_Data.city, Michigan_Population.population 
                    FROM Yelp_Data JOIN Michigan_Population ON Michigan_Population.city_name 
                    LIKE Yelp_Data.city''')
    conn.commit()
    cur.close()

def get_cities():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''SELECT DISTINCT city FROM All_Data''')
    result = cur.fetchall()
    cities_list = []
    for city in result:
        cities_list.append(city[0])
    return cities_list

def calculate_average_rating(cities_list):
    avg_rating_list = []
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    for city in cities_list:
        cur.execute('''SELECT AVG(rating) FROM All_Data WHERE city = ?''', (city,))
        result = cur.fetchall()
        avg_rating_list.append(round(result[0][0], 2))
    print(avg_rating_list)
    return avg_rating_list


def calculate_average_price(cities_list):
    avg_rating_list = []
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    for city in cities_list:
        cur.execute('''SELECT AVG(price) FROM All_Data WHERE city = ?''', (city,))
        result = cur.fetchall()
        avg_rating_list.append(round(result[0][0], 2))
    print(avg_rating_list)
    return avg_rating_list

def get_population(cities_list):
    population_list = []
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    for city in cities_list:
        cur.execute('''SELECT population FROM All_Data WHERE city = ?''', (city,))
        result = cur.fetchall()
        population_list.append(int(result[0][0].replace(',','')))
    print(population_list)
    return population_list

def rating_vs_population(ratingList, populationList):
    plt.style.use("seaborn")
    plt.title("Scatter plot of correlation between average rating of restaurants vs population of the cities in Michigan")
    plt.xlabel('Average population of citieis')
    plt.ylabel('Average rating of restaurants')
    plt.xlim((0,160000))
    plt.scatter(populationList, ratingList, s = 50, c = "green", edgecolors="black", linewidths=1, alpha=0.75)
    x = np.array(populationList)
    y = np.array(ratingList)
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b)
    plt.show()

def population_vs_cities_barh(citiesList, populationList):
    plt.style.use("seaborn")
    plt.title("Barchart of population of the cities in Michigan")
    plt.xlabel('Population')
    plt.ylabel('Population')
    plt.barh(citiesList, populationList)
    plt.show()

def price_vs_population(priceList, populationList):
    plt.style.use("seaborn")
    plt.title("Scatter plot of correlation between average price of restaurants vs population of the cities in Michigan")
    plt.xlabel('Average population of citieis')
    plt.ylabel('Average price of restaurants')
    plt.xlim((0,160000))
    plt.scatter(populationList, priceList, s = 50, c = "red", edgecolors="black", linewidths=1, alpha=0.75)
    x = np.array(populationList)
    y = np.array(priceList)
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b)
    plt.legend()
    plt.show()

def price_vs_rating(priceList, ratingList):
    plt.style.use("seaborn")
    plt.title("Scatter plot of correlation between average price vs average rating of restaurants in Michigan")
    plt.ylabel('Average rating of citieis')
    plt.xlabel('Average price of restaurants')
    plt.scatter(priceList, ratingList, s = 50, c = "blue", edgecolors="black", linewidths=1, alpha=0.75)
    x = np.array(priceList)
    y = np.array(ratingList)
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b)
    plt.show()    

def main():
    make_join()
    cities_list = get_cities()
    avg_rating_list = calculate_average_rating(cities_list)
    avg_price_list = calculate_average_price(cities_list)
    population_list = get_population(cities_list)
    population_vs_cities_barh(cities_list, population_list)
    rating_vs_population(avg_rating_list, population_list)
    price_vs_population(avg_price_list, population_list)
    price_vs_rating(avg_price_list, avg_rating_list)
    return 0

main()