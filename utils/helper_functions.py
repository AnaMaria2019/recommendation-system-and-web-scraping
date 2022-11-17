import time
import json
import pandas as pd

from selenium import webdriver


def load_dynamic_page(url, cool_down, browser_driver_path):
    # Retrieve the Web Page
    firefox = webdriver.Firefox(
        executable_path=browser_driver_path
    )
    get_height_string = 'return document.body.scrollHeight'
    scroll_command_string = 'window.scrollTo(0, document.body.scrollHeight);'

    # Gradually loading the dynamic content listed on nomadlist.com
    firefox.get(url)
    # Wait to load page
    time.sleep(cool_down)
    # Get scroll height
    prev_h = firefox.execute_script(get_height_string)
    check = True

    while check:
        # Scroll down to bottom
        firefox.execute_script(scroll_command_string)
        # Wait to load page
        time.sleep(cool_down)
        # Get scroll height
        curr_h = firefox.execute_script(get_height_string)
        check = (prev_h != curr_h)
        prev_h = curr_h

    firefox.execute_script(scroll_command_string)
    web_page = firefox.page_source
    firefox.close()

    return web_page


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


def convert_string_to_have_only_letters(string):
    new_string = ''

    for character in string:
        if character.isalpha():
            new_string += character

    return new_string


def convert_string_to_int(s):
    n = 0
    for c in s:
        if c.isdigit():
            n = n * 10 + int(c)
        elif c == ',':
            break

    return n


def convert_string_to_float(s):
    new_string = ''
    for c in s:
        if c == ',':
            new_string += '.'
        else:
            new_string += c

    return float(new_string)


def read_data_from_json(file_path, city_features):
    with open(file_path) as js:
        loaded_json = json.load(js)
        dataframe = pd.DataFrame(columns=city_features)

        cities = []
        # Dictionary of cities name with their corresponding line index in the pandas matrix
        line_idx_in_dataframe = {}

        pandas_index = 0
        num_cols = len(city_features)
        for line in loaded_json:
            pandas_line = []
            current_dict = line['fields']
            current_city = current_dict['city']

            if len(current_dict) < num_cols + 1:
                continue

            for feature_name in city_features:
                pandas_line.append(current_dict[feature_name])

            cities.append(current_city)
            line_idx_in_dataframe[current_city] = pandas_index
            dataframe.loc[pandas_index] = pandas_line
            pandas_index += 1

        return dataframe, cities, line_idx_in_dataframe
