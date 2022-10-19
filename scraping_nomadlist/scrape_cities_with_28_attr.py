import requests
import time
import json

from selenium import webdriver
from bs4 import BeautifulSoup
from scraping_nomadlist.utils.cities_wanted_features import all_28_features
from scraping_nomadlist.utils import helper_functions


""" Json list """
data = []


""" Retrieve the Web Page """
page_url = 'https://nomadlist.com/'
cooldown = 3
firefox = webdriver.Firefox(
    executable_path='../geckodriver.exe'
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
    print(f"City Name: {city['data-slug']}")

    curr_city = city["data-slug"]
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
        attributes = {}
        cnt += 1
        list_of_dicts_attributes.append({"city": city["data-slug"], "attributes": []})
        curr_dict = list_of_dicts_attributes[cnt - 1]
        for r in rows:
            key = r.find('td', {"class": "key"}).text
            new_key = helper_functions.extract_text(key)
            curr_dict["attributes"].append(new_key)

            if new_key == "Overall Score":
                overall_score = r.find('div', {"class": "filling"}).find(
                    'span', {"xitemprop": "ratingValue"}, recursive=False).text
                if overall_score:
                    overall_score = float(overall_score)
                    attributes["overall_score"] = overall_score
                    print(f'Overall Score: {overall_score}')  # float

            if new_key == "Nomad Score":
                nomad_score = r.find('div', {"class": "filling"}).find('span', recursive=False).text
                if nomad_score:
                    nomad_score = float(nomad_score)
                    attributes["nomad_score"] = nomad_score
                    print(f'Nomad Score: {nomad_score}')  # float

            if new_key == "Quality of life score":
                quality_of_life_score = r.find('div', {"class": "rating"})
                if quality_of_life_score and quality_of_life_score.has_attr("data-value"):
                    quality_of_life_score = int(quality_of_life_score["data-value"][0])
                    attributes["quality_of_life_score"] = quality_of_life_score
                    print(f'Quality of Life Score: {quality_of_life_score}')  # int

            if new_key == "Family score":
                family_score = r.find('div', {"class": "rating"})
                if family_score and family_score.has_attr("data-value"):
                    family_score = int(family_score["data-value"][0])
                    attributes["family_score"] = family_score
                    print(f'Family Score: {family_score}')  # int

            if new_key == "Cost":
                cost = r.find('div', {"class": "filling"})
                if cost:
                    cost = cost.get_text()
                    cost = helper_functions.format_cost(cost)
                    attributes["cost"] = cost
                    print(f'Cost: {cost}')  # float

            if new_key == "Internet":
                internet = r.find('div', {"class": "rating"})
                if internet and internet.has_attr("class"):
                    internet = int(internet["class"][-1][1])
                    attributes["internet"] = internet
                    print(f'Internet: {internet}')  # int

            if new_key == "Fun":
                fun = r.find('div', {"class": "rating"})
                if fun and fun.has_attr("data-value"):
                    fun = int(fun["data-value"][0])
                    attributes["fun"] = fun
                    print(f'Fun: {fun}')  # int

            if new_key == "Temperature now":
                temperature = r.find('span', {"class": "metric"})
                if temperature:
                    temperature = temperature.get_text()
                    temperature = helper_functions.format_temperature(temperature)
                    attributes["temperature"] = temperature
                    print(f'Temperature: {temperature}')  # int

            if new_key == "Humidity now":
                humidity = r.find('div', {"class": "rating"})
                if humidity and humidity.has_attr("class"):
                    humidity = int(humidity["class"][-1][1])
                    attributes["humidity"] = humidity
                    print(f'Humidity: {humidity}')  # int

            if new_key == "Air quality now":
                air_quality = r.find('div', {"class": "rating"})
                if air_quality and air_quality.has_attr("class"):
                    air_quality = int(air_quality["class"][-1][1])
                    attributes["air_quality"] = air_quality
                    print(f'Air Quality: {air_quality}')  # int

            if new_key == "Safety":
                safety = r.find('div', {"class": "rating"})
                if safety and safety.has_attr("class"):
                    safety = int(safety["class"][-1][1])
                    attributes["safety"] = safety
                    print(f'Safety: {safety}')  # int

            if new_key == "Education level":
                education_level = r.find('div', {"class": "rating"})
                if education_level and education_level.has_attr("data-value"):
                    education_level = int(education_level["data-value"][0])
                    attributes["education_level"] = education_level
                    print(f'Education Level: {education_level}')  # int

            if new_key == "English speaking":
                english_speaking = r.find('div', {"class": "rating"})
                if english_speaking and english_speaking.has_attr("data-value"):
                    english_speaking = int(english_speaking["data-value"][0])
                    attributes["english_speaking"] = english_speaking
                    print(f'English Speaking: {english_speaking}')  # int

            if new_key == "Walkability":
                walkability = r.find('div', {"class": "rating"})
                if walkability and walkability.has_attr("data-value"):
                    walkability = int(walkability["data-value"][0])
                    attributes["walkability"] = walkability
                    print(f'Walkability: {walkability}')  # int

            if new_key == "Peace":
                peace = r.find('div', {"class": "rating"})
                if peace and peace.has_attr("data-value"):
                    peace = int(peace["data-value"][0])
                    attributes["peace"] = peace
                    print(f'Peace: {peace}')  # int

            if new_key == "Traffic safety":
                traffic_safety = r.find('div', {"class": "rating"})
                if traffic_safety and traffic_safety.has_attr("data-value"):
                    traffic_safety = int(traffic_safety["data-value"][0])
                    attributes["traffic_safety"] = traffic_safety
                    print(f'Traffic Safety: {traffic_safety}')  # int

            if new_key == "Hospitals" or new_key == "Healthcare":
                hospitals = r.find('div', {"class": "rating"})
                if hospitals and hospitals.has_attr("data-value"):
                    hospitals = int(hospitals["data-value"][0])
                    attributes["hospitals"] = hospitals
                    print(f'Hospitals: {hospitals}')  # int

            if new_key == "Happiness":
                happiness = r.find('div', {"class": "rating"})
                if happiness and happiness.has_attr("data-value"):
                    happiness = int(happiness["data-value"][0])
                    attributes["happiness"] = happiness
                    print(f'Happiness: {happiness}')  # int

            if new_key == "Nightlife":
                nightlife = r.find('div', {"class": "rating"})
                if nightlife and nightlife.has_attr("data-value"):
                    nightlife = int(nightlife["data-value"][0])
                    attributes["nightlife"] = nightlife
                    print(f'Nightlife: {nightlife}')  # int

            if new_key == "Free WiFi in city":
                free_wifi = r.find('div', {"class": "rating"})
                if free_wifi and free_wifi.has_attr("data-value"):
                    free_wifi = int(free_wifi["data-value"][0])
                    attributes["free_wifi"] = free_wifi
                    print(f'Free Wifi: {free_wifi}')  # int

            if new_key == "Places to work from":
                places_to_work = r.find('div', {"class": "rating"})
                if places_to_work and places_to_work.has_attr("data-value"):
                    places_to_work = int(places_to_work["data-value"][0])
                    attributes["places_to_work"] = places_to_work
                    print(f'Placess to Work: {places_to_work}')  # int

            if new_key == "AC or heating":
                ac_heating = r.find('div', {"class": "rating"})
                if ac_heating and ac_heating.has_attr("data-value"):
                    ac_heating = int(ac_heating["data-value"][0])
                    attributes["ac_heating"] = ac_heating
                    print(f'A/C or Heating: {ac_heating}')  # int

            if new_key == "Friendly to foreigners":
                friendly_for_foreigners = r.find('div', {"class": "rating"})
                if friendly_for_foreigners and friendly_for_foreigners.has_attr("data-value"):
                    friendly_for_foreigners = int(friendly_for_foreigners["data-value"][0])
                    attributes["friendly_for_foreigners"] = friendly_for_foreigners
                    print(f'Friendly for Foreigners: {friendly_for_foreigners}')  # int

            if new_key == "Freedom of speech":
                freedom_of_speech = r.find('div', {"class": "rating"})
                if freedom_of_speech and freedom_of_speech.has_attr("data-value"):
                    freedom_of_speech = int(freedom_of_speech["data-value"][0])
                    attributes["freedom_of_speech"] = freedom_of_speech
                    print(f'Freedom of Speech: {freedom_of_speech}')  # int

            if new_key == "Racial tolerance":
                racial_tolerance = r.find('div', {"class": "rating"})
                if racial_tolerance and racial_tolerance.has_attr("data-value"):
                    racial_tolerance = int(racial_tolerance["data-value"][0])
                    attributes["racial_tolerance"] = racial_tolerance
                    print(f'Racial Tolerance: {racial_tolerance}')  # int

            if new_key == "Female friendly":
                female_friendly = r.find('div', {"class": "rating"})
                if female_friendly and female_friendly.has_attr("data-value"):
                    female_friendly = int(female_friendly["data-value"][0])
                    attributes["female_friendly"] = female_friendly
                    print(f'Female Friendly: {female_friendly}')  # int

            if new_key == "LGBTQ friendly":
                lgbt_friendly = r.find('div', {"class": "rating"})
                if lgbt_friendly and lgbt_friendly.has_attr("data-value"):
                    lgbt_friendly = int(lgbt_friendly["data-value"][0])
                    attributes["lgbt_friendly"] = lgbt_friendly
                    print(f'LGBTQ Friendly: {lgbt_friendly}')  # int

            if new_key == "Startup Score":
                startup_score = r.find('div', {"class": "rating"})
                if startup_score and startup_score.has_attr("data-value"):
                    startup_score = int(startup_score["data-value"][0])
                    attributes["startup_score"] = startup_score
                    print(f'Startup Score: {startup_score}')  # int

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

        # print(f'City: {curr_city}')
        # print(f"Attributes: {curr_dict['attributes']}")


print(has_all_cities)
print(data)
print(f'Cities which have all the attributes: {has_all_cities}')
print(f'Data: {data}')

# Write the cities with max nr of attributes (stored in 'data') in a Json file (for the next step: analayze them)
with open('files/analyze_data.json', 'w') as outfile:
    json.dump(data, outfile)
