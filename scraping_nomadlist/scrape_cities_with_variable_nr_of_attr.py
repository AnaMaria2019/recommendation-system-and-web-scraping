import cloudscraper
import time
import json

from selenium import webdriver
from bs4 import BeautifulSoup
from scraping_nomadlist.utils.cities_wanted_features import selected_cities_features_2
from scraping_nomadlist.utils import helper_functions

"""
The scope of this Python script is to extract from nomadlist.com the list of cities which have the features 
we want to test for the clustering.

After analyzing the data using correlation, 3 potential lists of features for a city that enters in the clustering 
algorithm were chosen. For each list we extract the cities with that attributes from nomadlist.com and create a Json
file with them. Then for each Json file we test K-Means Clustering Alg. on the cities contained.

In the end, we keep the list that obtains the best clustering of the cities.
"""


""" Retrieve the Web Page """
url = 'https://nomadlist.com/'
reloads = 200  # set the number of times to reload
pause = 3      # initial time interval between reloads
driver = webdriver.Firefox(
    executable_path='../geckodriver.exe'
)

# Load Nomad list page and click to view all results
driver.get(url)
time.sleep(4)

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(pause)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
page = driver.page_source
driver.close()

""" List from which a Json file will be created """
data = []

""" Start working with BeautifulSoup """
soup = BeautifulSoup(page, 'html.parser')
city_list = soup.find('ul', {"class": "grid"})
cities = city_list.find_all('li', {"data-type": "city"})[:-1]

# Ignore cities with bugs
bugged_cities = [
    "{slug}",
    "essaouira",
    "la-paz-mexico",
    "san-jose-costa-rica",
    "la-serena",
    "cordoba-spain",
    "macau",
    "victoria-seychelles",
    "george-town-cayman-islands",
    "faisalabad"
]

session = cloudscraper.create_scraper()
session.max_redirects = 3000

list_of_wanted_features = [
    'Cost',
    # 'Fun',
    'Temperature now',
    'Humidity now',
    # 'Walkability',
]
has_all_cnt = 0

# List of lists, where each list contains the features of the current city in the order from cities.
cities_features = []

# List of the city names in the order from cities.
cities_names = []

# Helper list.
list_of_dicts_of_city_features = []
cnt = 0
for city in cities:
    curr_city = city['data-slug']
    print(f"City Name: {city['data-slug']}")

    if curr_city in bugged_cities:
        continue

    city_url = 'https://nomadlist.com/' + curr_city + '/'
    print(f'City URL: {city_url}')
    city_response = session.get(city_url)
    city_page = city_response.content

    city_soup = BeautifulSoup(city_page, 'html.parser')
    table = city_soup.find('table')
    if table:
        rows = table.find_all('tr')
    else:
        continue

    if rows:
        cnt += 1
        curr_city_features_key_value = {}
        list_of_dicts_of_city_features.append({"city": city["data-slug"], "features": []})
        curr_dict_of_city_features_key = list_of_dicts_of_city_features[cnt - 1]

        for r in rows:
            key = r.find('td', {"class": "key"}).text
            new_key = helper_functions.extract_text(key)
            curr_dict_of_city_features_key["features"].append(new_key)

            if new_key == "Cost":
                cost = r.find('div', {"class": "filling"})
                if cost:
                    cost = cost.get_text()
                    cost = helper_functions.format_cost(cost)
                    curr_city_features_key_value["cost"] = cost
                    print(f'Cost: {cost}')  # float

            """
            if new_key == "Fun":
                fun = r.find('div', {"class": "rating"})
                if fun and fun.has_attr("data-value"):
                    fun = int(fun["data-value"][0])
                    curr_city_features_key_value["fun"] = fun
                    print(f'Fun: {fun}')  # int
            """

            if new_key == "Temperature now":
                temperature = r.find('span', {"class": "metric"})
                if temperature:
                    temperature = temperature.get_text()
                    temperature = helper_functions.format_temperature(temperature)
                    curr_city_features_key_value["temperature"] = temperature
                    print(f'Temperature: {temperature}')  # int

            if new_key == "Humidity now":
                humidity = r.find('div', {"class": "filling"})
                if humidity:
                    humidity = humidity.get_text()
                    humidity = helper_functions.format_humidity(humidity)
                    curr_city_features_key_value["humidity"] = humidity
                    print(f'Humidity: {humidity}')  # int

            """
            if new_key == "Walkability":
                walkability = r.find('div', {"class": "rating"})
                if walkability and walkability.has_attr("data-value"):
                    walkability = int(walkability["data-value"][0])
                    curr_city_features_key_value["walkability"] = walkability
                    print(f'Walkability: {walkability}')  # int
            """

        has_all = True
        for feature in selected_cities_features_2:
            if feature not in curr_dict_of_city_features_key["features"]:
                has_all = False
                break

        if has_all:
            has_all_cnt += 1
            # PUT IN DATA EVERY CITY WHICH HAS ALL THE ATTRIBUTES FROM WANTED_ATTRIBUTES.
            # FROM DATA A JSON FILE WILL BE CREATED FOR POPULATING THE APPLICATION'S DATABASE WITH.
            print(f'City: {curr_city}')
            data.append({"model": "app.city", "pk": has_all_cnt, "fields": {}})
            curr_dict_1 = data[has_all_cnt - 1]

            curr_dict_1["fields"]["cost"] = curr_city_features_key_value["cost"]
            # curr_dict_1["fields"]["fun"] = curr_city_features_key_value["fun"]
            curr_dict_1["fields"]["temperature"] = curr_city_features_key_value["temperature"]
            curr_dict_1["fields"]["humidity"] = curr_city_features_key_value["humidity"]
            # curr_dict_1["fields"]["walkability"] = curr_city_features_key_value["walkability"]
            curr_dict_1["fields"]["city"] = curr_city

        # print(f'City: {curr_city}')
        # print(f"Features: {curr_dict_of_city_features_key['features']}")

print(f'Data: {data}')

with open('files/temp-1.json', 'w') as outfile:
    json.dump(data, outfile)
