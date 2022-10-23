"""
    LOGIC PROCESS:
        The scope of this Python script is to extract from nomadlist.com the list of cities that have the features
        we want to test for clustering.

        After analyzing all possible features that a city might hvae, using correlation, 3 potential lists of features
        for a city that enters in the clustering algorithm were chosen. For each list, using this script, we extract
        the cities with that attributes from nomadlist.com and create a Json file with them. Then for each Json file
        we test K-Means Clustering Alg.

        In the end, we keep the list that obtains the best clustering of the cities. Also the Json file associated with
        the winning list will be later used for populating the application's database.

    NOTE:
        Replace the list imported from 'cities_wanted_features.py' module with the one for which you want to make
        the scraping.
"""

import cloudscraper
import json

from bs4 import BeautifulSoup
from scraping_nomadlist.utils.cities_wanted_features import selected_cities_features_1 as city_features
from scraping_nomadlist.utils import helper_functions


if __name__ == '__main__':
    # List from which a Json file will be created
    data = []

    # Retrieve the Web Page
    nomad_page = helper_functions.load_dynamic_page(
        url='https://nomadlist.com/',
        cool_down=3,
        browser_driver_path='../geckodriver.exe'
    )

    # Start working with BeautifulSoup
    soup = BeautifulSoup(nomad_page, 'html.parser')
    city_list = soup.find('ul', {'class': 'grid'})
    cities = city_list.find_all('li', {'data-type': 'city'})[:-1]

    # Ignore cities with bugs
    bugged_cities = [
        '{slug}', 'essaouira', 'la-paz-mexico', 'san-jose-costa-rica',
        'la-serena', 'cordoba-spain', 'macau', 'victoria-seychelles',
        'george-town-cayman-islands', 'faisalabad'
    ]

    session = cloudscraper.create_scraper()
    session.max_redirects = 3000

    city_id = 0

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
            curr_city_features = {}

            if len(city_features) == 5:
                # list 1 = ['cost', 'temperature', 'humidity', 'fun', 'walkability']
                keys_with_div_attr_data_value_pattern = {
                    'Fun': 'fun',
                    'Walkability': 'walkability'
                }
            elif len(city_features) == 4:
                # list 2 = ['cost', 'temperature', 'humidity', 'fun']
                keys_with_div_attr_data_value_pattern = {'Fun': 'fun'}
            else:
                # list 3 = ['cost', 'temperature', 'humidity']
                keys_with_div_attr_data_value_pattern = {}

            for r in rows:
                key = r.find('td', {'class': 'key'}).text
                new_key = helper_functions.extract_text(key)

                if new_key in keys_with_div_attr_data_value_pattern:
                    feature_name = keys_with_div_attr_data_value_pattern[new_key]
                    feature_field = r.find('div', {'class': 'rating'})
                    if feature_field and feature_field.has_attr('data-value'):
                        feature_value = int(feature_field['data-value'][0])
                        curr_city_features[feature_name] = feature_value
                        print(f'{feature_name}: {feature_value}')  # int

                if new_key == 'Cost':
                    feature_name = 'cost'
                    cost_text = r.find('div', {'class': 'filling'}).get_text()
                    if cost_text:
                        cost_value = helper_functions.format_cost(cost_text)
                        curr_city_features[feature_name] = cost_value
                        print(f'{feature_name}: {cost_value}')  # float

                if new_key == 'Temperature now':
                    feature_name = 'temperature'
                    temperature_text = r.find('span', {'class': 'metric'}).get_text()
                    if temperature_text:
                        temperature_value = helper_functions.format_temperature(temperature_text)
                        curr_city_features[feature_name] = temperature_value
                        print(f'{feature_name}: {temperature_value}')  # int

                if new_key == 'Humidity now':
                    feature_name = 'humidity'
                    humidity_text = r.find('div', {'class': 'filling'}).get_text()
                    if humidity_text:
                        humidity_value = helper_functions.format_humidity(humidity_text)
                        curr_city_features[feature_name] = humidity_value
                        print(f'{feature_name}: {humidity_value}')  # int

            has_all_features = True
            for feature in city_features:
                if feature not in curr_city_features:
                    has_all_features = False
                    break

            if has_all_features:
                city_id += 1
                data.append({'model': 'app.city', 'pk': city_id, 'fields': {}})
                features_dict = data[-1]['fields']

                features_dict['city'] = curr_city
                for feature_name in city_features:
                    features_dict[feature_name] = curr_city_features[feature_name]

    print(f'Data: {data}')

    with open('files/temp-1.json', 'w') as outfile:
        json.dump(data, outfile)
