import requests
import time
import json

from selenium import webdriver
from bs4 import BeautifulSoup
from .utils.cities_wanted_features import all_28_features

""" Helper functions """


def extract_text(s):
    new_string = ""

    for c in s:
        if c.isalpha():
            new_string = new_string + c
        elif c.isspace():
            new_string = new_string + c

    return new_string.lstrip()


def string_to_int(s):
    n = 0
    for c in s:
        if c.isdigit():
            n = n * 10 + int(c)

    return n


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
# END


""" Json list """
data = []


""" Retrieve the Web Page """

page_url = 'https://nomadlist.com/'
cooldown = 3
firefox = webdriver.Firefox(
    executable_path=
    "\\1_Ana\\3_Info\\11_Facultate\\1_Licenta\\Lucrare_de_Licenta\\1_Aplicatie\\RecSystem_and_WebScraping\\geckodriver.exe"
)
get_height_string = "return document.body.scrollHeight"
scroll_command_string = "window.scrollTo(0, document.body.scrollHeight);"

# Incarcam treptat continutul dinamic de pe Nomadlist
firefox.get(page_url)
time.sleep(cooldown)
prev_h = firefox.execute_script(get_height_string)
curr_h = 0
check = True

while check is True:
    firefox.execute_script(scroll_command_string)
    time.sleep(cooldown)
    curr_h = firefox.execute_script(get_height_string)
    check = (prev_h != curr_h)
    prev_h = curr_h

firefox.execute_script(scroll_command_string)
nomad_page = firefox.page_source
firefox.close()


""" Start working with BeautifulSoup """

soup = BeautifulSoup(nomad_page, 'html.parser')
city_list = soup.find('ul', {"class": "grid"})
cities = city_list.find_all('li', {"data-type": "city"})[:-1]

city_features = []
city_names = []
bugged_cities = ["{slug}", "essaouira", "la-paz-mexico",
                 "san-jose-costa-rica", "la-serena", "cordoba-spain",
                 "macau", "victoria-seychelles", "george-town-cayman-islands", "faisalabad"]

session = requests.Session()
session.max_redirects = 3000

has_all_cities = []
all_cnt = 0

cnt = 0
list_of_dicts_attributes = []
for city in cities:
    print("City Name: {}".format(city["data-slug"]))

    curr_city = city["data-slug"]
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
        attributes = {}
        cnt += 1
        list_of_dicts_attributes.append({"city": city["data-slug"], "attributes": []})
        curr_dict = list_of_dicts_attributes[cnt - 1]
        for r in rows:
            key = r.find('td', {"class": "key"}).text
            new_key = extract_text(key)
            curr_dict["attributes"].append(new_key)

            if new_key == "Overall Score":
                overall_score = r.find('div', {"class": "filling"}).find(
                    'span', {"xitemprop": "ratingValue"}, recursive=False).text
                if overall_score:
                    overall_score = float(overall_score)
                    attributes["overall_score"] = overall_score
                    print("Overall Score: {}".format(overall_score))  # float

            if new_key == "Nomad Score":
                nomad_score = r.find('div', {"class": "filling"}).find('span', recursive=False).text
                if nomad_score:
                    nomad_score = float(nomad_score)
                    attributes["nomad_score"] = nomad_score
                    print("Nomad Score: {}".format(nomad_score))  # float

            if new_key == "Quality of life score":
                quality_of_life_score = r.find('div', {"class": "rating"})
                if quality_of_life_score and quality_of_life_score.has_attr("data-value"):
                    quality_of_life_score = int(quality_of_life_score["data-value"][0])
                    attributes["quality_of_life_score"] = quality_of_life_score
                    print("Quality of Life Score: {}".format(quality_of_life_score))  # int

            if new_key == "Family score":
                family_score = r.find('div', {"class": "rating"})
                if family_score and family_score.has_attr("data-value"):
                    family_score = int(family_score["data-value"][0])
                    attributes["family_score"] = family_score
                    print("Family Score: {}".format(family_score))  # int

            if new_key == "Cost":
                cost = r.find('div', {"class": "filling"})
                if cost:
                    cost = cost.get_text()
                    cost = format_cost(cost)
                    attributes["cost"] = cost
                    print("Cost: {}".format(cost))  # float

            if new_key == "Internet":
                internet = r.find('div', {"class": "rating"})
                if internet and internet.has_attr("class"):
                    internet = int(internet["class"][-1][1])
                    attributes["internet"] = internet
                    print("Internet: {}".format(internet))  # int

            if new_key == "Fun":
                fun = r.find('div', {"class": "rating"})
                if fun and fun.has_attr("data-value"):
                    fun = int(fun["data-value"][0])
                    attributes["fun"] = fun
                    print("Fun: {}".format(fun))  # int

            if new_key == "Temperature now":
                temperature = r.find('span', {"class": "metric"})
                if temperature:
                    temperature = temperature.get_text()
                    temperature = format_temperature(temperature)
                    attributes["temperature"] = temperature
                    print("Temperature: {}".format(temperature))  # int

            if new_key == "Humidity now":
                humidity = r.find('div', {"class": "rating"})
                if humidity and humidity.has_attr("class"):
                    humidity = int(humidity["class"][-1][1])
                    attributes["humidity"] = humidity
                    print("Humidity: {}".format(humidity))  # int

            if new_key == "Air quality now":
                air_quality = r.find('div', {"class": "rating"})
                if air_quality and air_quality.has_attr("class"):
                    air_quality = int(air_quality["class"][-1][1])
                    attributes["air_quality"] = air_quality
                    print("Air Quality: {}".format(air_quality))  # int

            if new_key == "Safety":
                safety = r.find('div', {"class": "rating"})
                if safety and safety.has_attr("class"):
                    safety = int(safety["class"][-1][1])
                    attributes["safety"] = safety
                    print("Safety: {}".format(safety))  # int

            if new_key == "Education level":
                education_level = r.find('div', {"class": "rating"})
                if education_level and education_level.has_attr("data-value"):
                    education_level = int(education_level["data-value"][0])
                    attributes["education_level"] = education_level
                    print("Education Level: {}".format(education_level))  # int

            if new_key == "English speaking":
                english_speaking = r.find('div', {"class": "rating"})
                if english_speaking and english_speaking.has_attr("data-value"):
                    english_speaking = int(english_speaking["data-value"][0])
                    attributes["english_speaking"] = english_speaking
                    print("English Speaking: {}".format(english_speaking))  # int

            if new_key == "Walkability":
                walkability = r.find('div', {"class": "rating"})
                if walkability and walkability.has_attr("data-value"):
                    walkability = int(walkability["data-value"][0])
                    attributes["walkability"] = walkability
                    print("Walkability: {}".format(walkability))  # int

            if new_key == "Peace":
                peace = r.find('div', {"class": "rating"})
                if peace and peace.has_attr("data-value"):
                    peace = int(peace["data-value"][0])
                    attributes["peace"] = peace
                    print("Peace: {}".format(peace))  # int

            if new_key == "Traffic safety":
                traffic_safety = r.find('div', {"class": "rating"})
                if traffic_safety and traffic_safety.has_attr("data-value"):
                    traffic_safety = int(traffic_safety["data-value"][0])
                    attributes["traffic_safety"] = traffic_safety
                    print("Traffic Safety: {}".format(traffic_safety))  # int

            if new_key == "Hospitals" or new_key == "Healthcare":
                hospitals = r.find('div', {"class": "rating"})
                if hospitals and hospitals.has_attr("data-value"):
                    hospitals = int(hospitals["data-value"][0])
                    attributes["hospitals"] = hospitals
                    print("Hospitals: {}".format(hospitals))  # int

            if new_key == "Happiness":
                happiness = r.find('div', {"class": "rating"})
                if happiness and happiness.has_attr("data-value"):
                    happiness = int(happiness["data-value"][0])
                    attributes["happiness"] = happiness
                    print("Happiness: {}".format(happiness))  # int

            if new_key == "Nightlife":
                nightlife = r.find('div', {"class": "rating"})
                if nightlife and nightlife.has_attr("data-value"):
                    nightlife = int(nightlife["data-value"][0])
                    attributes["nightlife"] = nightlife
                    print("Nightlife: {}".format(nightlife))  # int

            if new_key == "Free WiFi in city":
                free_wifi = r.find('div', {"class": "rating"})
                if free_wifi and free_wifi.has_attr("data-value"):
                    free_wifi = int(free_wifi["data-value"][0])
                    attributes["free_wifi"] = free_wifi
                    print("Free Wifi: {}".format(free_wifi))  # int

            if new_key == "Places to work from":
                places_to_work = r.find('div', {"class": "rating"})
                if places_to_work and places_to_work.has_attr("data-value"):
                    places_to_work = int(places_to_work["data-value"][0])
                    attributes["places_to_work"] = places_to_work
                    print("Placess to Work: {}".format(places_to_work))  # int

            if new_key == "AC or heating":
                ac_heating = r.find('div', {"class": "rating"})
                if ac_heating and ac_heating.has_attr("data-value"):
                    ac_heating = int(ac_heating["data-value"][0])
                    attributes["ac_heating"] = ac_heating
                    print("A/C or Heating: {}".format(ac_heating))  # int

            if new_key == "Friendly to foreigners":
                friendly_for_foreigners = r.find('div', {"class": "rating"})
                if friendly_for_foreigners and friendly_for_foreigners.has_attr("data-value"):
                    friendly_for_foreigners = int(friendly_for_foreigners["data-value"][0])
                    attributes["friendly_for_foreigners"] = friendly_for_foreigners
                    print("Friendly for Foreigners: {}".format(friendly_for_foreigners))  # int

            if new_key == "Freedom of speech":
                freedom_of_speech = r.find('div', {"class": "rating"})
                if freedom_of_speech and freedom_of_speech.has_attr("data-value"):
                    freedom_of_speech = int(freedom_of_speech["data-value"][0])
                    attributes["freedom_of_speech"] = freedom_of_speech
                    print("Freedom of Speech: {}".format(freedom_of_speech))  # int

            if new_key == "Racial tolerance":
                racial_tolerance = r.find('div', {"class": "rating"})
                if racial_tolerance and racial_tolerance.has_attr("data-value"):
                    racial_tolerance = int(racial_tolerance["data-value"][0])
                    attributes["racial_tolerance"] = racial_tolerance
                    print("Racial Tolerance: {}".format(racial_tolerance))  # int

            if new_key == "Female friendly":
                female_friendly = r.find('div', {"class": "rating"})
                if female_friendly and female_friendly.has_attr("data-value"):
                    female_friendly = int(female_friendly["data-value"][0])
                    attributes["female_friendly"] = female_friendly
                    print("Female Friendly: {}".format(female_friendly))  # int

            if new_key == "LGBTQ friendly":
                lgbt_friendly = r.find('div', {"class": "rating"})
                if lgbt_friendly and lgbt_friendly.has_attr("data-value"):
                    lgbt_friendly = int(lgbt_friendly["data-value"][0])
                    attributes["lgbt_friendly"] = lgbt_friendly
                    print("LGBTQ Friendly: {}".format(lgbt_friendly))  # int

            if new_key == "Startup Score":
                startup_score = r.find('div', {"class": "rating"})
                if startup_score and startup_score.has_attr("data-value"):
                    startup_score = int(startup_score["data-value"][0])
                    attributes["startup_score"] = startup_score
                    print("Startup Score: {}".format(startup_score))  # int

        has_all = True
        for attribute in all_28_features:
            if ((attribute == "Hospitals") and (attribute not in curr_dict["attributes"]) \
                    and ("Healthcare" not in curr_dict["attributes"])) or (attribute not in curr_dict["attributes"]):
                has_all = False
                break

        print(has_all)
        print()
        if has_all:
            all_cnt += 1
            # PUT IN DATA EVERY CITY WHICH HAS ALL THE ATTRIBUTES FROM ALL_28_FEATURES.
            # USE THESE CITIES FOR THE CORRELATION AND HEATMAP.
            # CHOOSE THE ATTRIBUTES THAT ARE LESS CORRELATED.
            # TAKE ALL CITIES THAT HAVE THOSE ATTRIBUTES AND MAKE A JSON FOR POPULATING THE DATABASE WITH.
            has_all_cities.append({"city": curr_dict["city"], "url": city_url})
            data.append({"nr": all_cnt, "city": curr_city, "fields": {}})
            curr_dict_1 = data[all_cnt - 1]
            curr_dict_1["fields"]["overall_score"] = attributes["overall_score"]
            # curr_dict_1["fields"]["nomad_score"] = attributes["nomad_score"]
            curr_dict_1["fields"]["quality_of_life_score"] = attributes["quality_of_life_score"]
            curr_dict_1["fields"]["family_score"] = attributes["family_score"]
            curr_dict_1["fields"]["cost"] = attributes["cost"]
            curr_dict_1["fields"]["internet"] = attributes["internet"]
            curr_dict_1["fields"]["fun"] = attributes["fun"]
            curr_dict_1["fields"]["temperature"] = attributes["temperature"]
            curr_dict_1["fields"]["humidity"] = attributes["humidity"]
            curr_dict_1["fields"]["air_quality"] = attributes["air_quality"]
            curr_dict_1["fields"]["safety"] = attributes["safety"]
            curr_dict_1["fields"]["education_level"] = attributes["education_level"]
            curr_dict_1["fields"]["english_speaking"] = attributes["english_speaking"]
            curr_dict_1["fields"]["walkability"] = attributes["walkability"]
            curr_dict_1["fields"]["peace"] = attributes["peace"]
            curr_dict_1["fields"]["traffic_safety"] = attributes["traffic_safety"]
            curr_dict_1["fields"]["hospitals"] = attributes["hospitals"]
            curr_dict_1["fields"]["happiness"] = attributes["happiness"]
            curr_dict_1["fields"]["nightlife"] = attributes["nightlife"]
            curr_dict_1["fields"]["free_wifi"] = attributes["free_wifi"]
            curr_dict_1["fields"]["places_to_work"] = attributes["places_to_work"]
            curr_dict_1["fields"]["ac_heating"] = attributes["ac_heating"]
            curr_dict_1["fields"]["friendly_for_foreigners"] = attributes["friendly_for_foreigners"]
            curr_dict_1["fields"]["freedom_of_speech"] = attributes["freedom_of_speech"]
            curr_dict_1["fields"]["racial_tolerance"] = attributes["racial_tolerance"]
            curr_dict_1["fields"]["female_friendly"] = attributes["female_friendly"]
            curr_dict_1["fields"]["lgbt_friendly"] = attributes["lgbt_friendly"]
            curr_dict_1["fields"]["startup_score"] = attributes["startup_score"]

        # print("City: {}".format(curr_city))
        # print("Attributes: {}".format(curr_dict["attributes"]))


print(has_all_cities)
print(data)
print("Cities which have all the attributes: {}".format(has_all_cities))
print("Data: {}".format(data))

# Write the cities with max nr of attributes (stored in 'data') in a Json file (for the next step: analayze them)
with open('files/analyze_data.json', 'w') as outfile:
    json.dump(data, outfile)
