import cloudscraper
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import json
from .cities_wanted_features import selected_cities_features_2

"""
The scope of this Python script is to extract from nomadlist.com the list of cities which have the features 
we want to test for the clustering.

After analyzing the data using correlation, 3 potential lists of features for a city that enters in the clustering 
algorithm were chosen. For each list we extract the cities with that attributes from nomadlist.com and create a Json
file with them. Then for each Json file we test K-Means Clustering Alg. on the cities contained.

In the end, we keep the list that obtains the best clustering of the cities.
"""


# START: Helper functions
def extract_text(s):
    new_string = ""

    for c in s:
        if c.isalpha():
            new_string = new_string + c
        elif c.isspace():
            new_string = new_string + c

    return new_string.lstrip()


def format_cost(string_cost):
    new_cost = ''

    for c in string_cost:
        if c.isdigit():
            new_cost = new_cost + c

    new_cost = float(new_cost)

    return new_cost


def format_temperature(temp):
    new_temp = 0

    for c in temp:
        if c.isdigit():
            new_temp = new_temp * 10 + int(c)

    return new_temp


def format_humidity(humidity_text):
    new_humidity = 0

    for c in humidity_text:
        if c.isdigit():
            new_humidity = new_humidity * 10 + int(c)

    return new_humidity
# END


""" Retrieve the Web Page """

url = 'https://nomadlist.com/'
reloads = 200  # set the number of times to reload
pause = 3      # initial time interval between reloads
driver = webdriver.Firefox(
    executable_path=
    "\\1_Ana\\3_Info\\11_Facultate\\1_Licenta\\Lucrare_de_Licenta\\1_Aplicatie\\RecSystem_and_WebScraping\\geckodriver.exe"
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
    curr_city = city["data-slug"]
    print("City Name: {}".format(city["data-slug"]))

    if curr_city in bugged_cities:
        continue

    city_url = 'https://nomadlist.com/' + curr_city + '/'
    print("City URL: {}".format(city_url))
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
            new_key = extract_text(key)
            curr_dict_of_city_features_key["features"].append(new_key)

            if new_key == "Cost":
                cost = r.find('div', {"class": "filling"})
                if cost:
                    cost = cost.get_text()
                    cost = format_cost(cost)
                    curr_city_features_key_value["cost"] = cost
                    print("Cost: {}".format(cost))  # float

            """
            if new_key == "Fun":
                fun = r.find('div', {"class": "rating"})
                if fun and fun.has_attr("data-value"):
                    fun = int(fun["data-value"][0])
                    curr_city_features_key_value["fun"] = fun
                    print("Fun: {}".format(fun))  # int
            """

            if new_key == "Temperature now":
                temperature = r.find('span', {"class": "metric"})
                if temperature:
                    temperature = temperature.get_text()
                    temperature = format_temperature(temperature)
                    curr_city_features_key_value["temperature"] = temperature
                    print("Temperature: {}".format(temperature))  # int

            if new_key == "Humidity now":
                humidity = r.find('div', {"class": "filling"})
                if humidity:
                    humidity = humidity.get_text()
                    humidity = format_humidity(humidity)
                    curr_city_features_key_value["humidity"] = humidity
                    print("Humidity: {}".format(humidity))  # int

            """
            if new_key == "Walkability":
                walkability = r.find('div', {"class": "rating"})
                if walkability and walkability.has_attr("data-value"):
                    walkability = int(walkability["data-value"][0])
                    curr_city_features_key_value["walkability"] = walkability
                    print("Walkability: {}".format(walkability))  # int
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
            print("City: {}".format(curr_city))
            data.append({"model": "app.city", "pk": has_all_cnt, "fields": {}})
            curr_dict_1 = data[has_all_cnt - 1]

            curr_dict_1["fields"]["cost"] = curr_city_features_key_value["cost"]
            # curr_dict_1["fields"]["fun"] = curr_city_features_key_value["fun"]
            curr_dict_1["fields"]["temperature"] = curr_city_features_key_value["temperature"]
            curr_dict_1["fields"]["humidity"] = curr_city_features_key_value["humidity"]
            # curr_dict_1["fields"]["walkability"] = curr_city_features_key_value["walkability"]
            curr_dict_1["fields"]["city"] = curr_city

        # print("City: {}".format(curr_city))
        # print("Features: {}".format(curr_dict_of_city_features_key["features"]))

print("Data: {}".format(data))

with open('Files/test_1.json', 'w') as outfile:
    json.dump(data, outfile)
