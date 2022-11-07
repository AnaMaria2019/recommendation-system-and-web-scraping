"""
    LOGIC PROCESS:
        The scope of this Python script is to create the final fixture that will be used in the PennyTravel
        application to populate the database. The cities data used in this script is read from the file
        that obtained the best clustering score, in this case, the file that stores the cities from
        nomadlist.com with ['cost', 'temperature', 'humidity'] features.

        The first step in creating the final fixture file is to extract from nationsonline.org the first found
        airport code for each city. Unfortunately, an airport code was not found for all cities, but this script
        helps significantly. For the cities remained without airport code, manual action is necessary to have the
        final fixture completed.

        The next step, is to also add the image path for each city in the final fixture (in the PennyTravel
        application an image will be stored for each city and it will be needed to have attached to the final fixture
        the path where it will be stored).

    NOTE:
        On nationsonline.org there are multiple cities different from each other that have the same name
        (example: 'Athens, Hellinikon Airport' which is Athens from Greece and 'Athens (GA)' which is one
        of the cities called Athens from USA) and this script will not differentiate the cities by their location
        on the map, resulting in possible wrong airport code associated with the wrong city.

        For this matter, after creating the final fixture, a manual check in the final fixture for airport codes
        is necessary.
"""


import time
import json

from selenium import webdriver
from bs4 import BeautifulSoup

from scraping_nomadlist.utils import helper_functions


def retrieve_web_page(url, cooldown, browser_driver_path):
    # Retrieve the page which contains all the IATA Codes of all registered airports
    firefox = webdriver.Firefox(
        executable_path=browser_driver_path
    )
    firefox.get(url)
    # Sleep 'cooldown' seconds in order to let the page finish loading
    time.sleep(cooldown)
    web_page = firefox.page_source
    firefox.close()

    return web_page


def load_data_and_create_airports_dict(file_path):
    input_data = []
    # NOTE: Because a city can have multiple airports associated to it, we are going to only extract
    #       the first one found, for this matter, a dictionary of cities' airports is used to check
    #       if it has already been found a IATA code (airport code) for a city.
    airports = {}

    with open(file_path) as input_file:
        loaded_json = json.load(input_file)

        for line in loaded_json:
            input_data.append(line)
            current_city_info = line['fields']
            current_city_name = current_city_info['city']
            # Initially we don't know any airport code for the cities
            airports[current_city_name] = ''

    return input_data, airports


def add_airport_code_and_image_path_to_cities(cities_data, airports):
    for line in cities_data:
        current_city_info = line['fields']
        current_city_name = current_city_info['city']

        current_city_info['city_code'] = airports[current_city_name]
        if 'image' not in current_city_info or current_city_info['image'] == '':
            current_city_info['image'] = '/media/' + current_city_name + '.jpg'

    return cities_data


def write_to_output_file(cities_data, file_path):
    with open(file_path, 'w') as output_file:
        json.dump(cities_data, output_file)


if __name__ == '__main__':
    input_file_path = 'recommendation_system/files/test-3/fixture-test-3.json'
    output_file_path = 'final-fixture.json'

    data, airports_code = load_data_and_create_airports_dict(
        file_path=input_file_path
    )

    airport_codes_page = retrieve_web_page(
        url='https://www.nationsonline.org/oneworld/IATA_Codes/airport_code_list.htm',
        cooldown=2,
        browser_driver_path='geckodriver.exe'
    )

    # Use BeautifulSoup to extract only the div elements that contain the airports codes
    # (the codes are arranged in alphabetical order, each letter has associated to it
    # a div element with the id the letter itself)
    soup = BeautifulSoup(airport_codes_page, 'html.parser')
    alphabet_divs = soup.find_all(
        'div', {'id': [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', 'L',
            'M', 'N', 'O', 'P', 'Q', 'R',
            'S', 'T', 'U', 'V', 'W', 'XYZ',
        ]}
    )
    for div in alphabet_divs:
        table = div.find('table')

        if table:
            rows = table.find_all('tr')

            if rows:
                # The rows that present interest are from index 2 to len(rows) - 1
                # (first two rows contain the alphabet letter and a border)
                for idx in range(2, len(rows)):
                    current_row_columns = rows[idx].find_all('td')
                    airport_name_column = current_row_columns[0]
                    airport_name = airport_name_column.get_text()
                    airport_name = helper_functions.convert_string_to_have_only_letters(
                        string=airport_name.lower()
                    )

                    airport_code_column = current_row_columns[-1]
                    airport_code = airport_code_column.get_text()
                    # print(f'Airport: {airport_name} has IATA code: {airport_code}')

                    for city in airports_code:
                        # NOTE: It is possible to have cities names that don't contain only letters, for this
                        #       matter we convert them in order to be sure they can be compared with the name
                        #       of the airport (every airport name contains the name of its associated city)
                        city_name = helper_functions.convert_string_to_have_only_letters(city)

                        if airports_code[city] == ''\
                                and city_name in airport_name\
                                and airport_name.startswith(city_name):
                            airports_code[city] = airport_code

    final_data = add_airport_code_and_image_path_to_cities(
        cities_data=data,
        airports=airports_code
    )

    write_to_output_file(
        cities_data=final_data,
        file_path=output_file_path
    )
