import time
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

""" Helper functions"""


def only_letters(name):
    only_letters_name = ""

    for c in name:
        if c.isalpha():
            only_letters_name = only_letters_name + c

    return only_letters_name


# print(only_letters("n'djamena"))
# test = only_letters("n'djamenaanabanana")
# print(test.startswith("ndjamena"))

""" Initialize a dict of cities to check if it has already been found a IATA code for a city. \
Some cities may have multiple airports, we want only the code for the city (it is enough to search \
flights for all the airports in the city) """
cities = {}

with open('Files/fixture_1.json') as js:
    loaded_json = json.load(js)

    for line in loaded_json:
        curr_dict = line['fields']
        city = curr_dict['city']
        cities[city] = ''

# print(cities)

""" Retrieve the page which contains all the IATA Codes of all the airports """
url = 'https://www.nationsonline.org/oneworld/IATA_Codes/airport_code_list.htm'
driver = webdriver.Firefox(
    executable_path='../geckodriver.exe'
)
driver.get(url)

""" Sleep 1.5 seconds in order to let the page finishing to load """
time.sleep(1.5)
page = driver.page_source
driver.close()

""" Use BeautifulSoup to extract only the divs that contain the airports codes """
soup = BeautifulSoup(page, 'html.parser')
alphabet_divs = soup.find_all(
    'div', {'id': [
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'O',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'XYZ',
    ]}
)
# print(alphabet_divs)
for div in alphabet_divs:
    table = div.find('table')

    if table:
        rows = table.find_all('tr')

        if rows:
            """ 
            The rows that present interest are from index 2 -> len(rows) \
            (first two rows contain the alphabet letter and a border)
            """
            for ind in range(2, len(rows)):
                first_td = rows[ind].find('td')
                airport_name = first_td.get_text()  # This function gets all the text in the td tag
                lower_airport_name = airport_name.lower()
                only_letters_airport_name = only_letters(lower_airport_name)

                last_td = rows[ind].find_all('td')[-1]
                airport_code = last_td.get_text()

                # print(f'Airport: {lower_airport_name} has IATA code: {airport_code}')

                for key in cities:
                    only_letters_key = only_letters(key)

                    if cities[key] == '' and only_letters_key in only_letters_airport_name \
                            and only_letters_airport_name.startswith(only_letters_key):
                        cities[key] = airport_code
                        # print(only_letters_airport_name)
        # print(table)

print(cities)

data = []

with open('Files/fixture_1.json') as js:
    loaded_json = json.load(js)

    """ See how many cities don't have an airport code associated (RESULT = 603)"""
    cnt = 0
    for key in cities:
        if cities[key] == '':
            cnt += 1
            # print(key)

    # print(cnt)

    nr = 0
    for line in loaded_json:
        nr += 1
        data.append(line)
        curr_dict = data[nr-1]

        city = curr_dict['fields']['city']
        # if cities[city] != '':
        curr_dict['fields']['city_code'] = cities[city]

        if "image" not in curr_dict['fields'] or curr_dict['fields']['image'] == "":
            curr_dict['fields']['image'] = "/media/" + city + ".jpg"

    print(data)

with open('Files/final_fixture.json', 'w') as js:
    json.dump(data, js)
