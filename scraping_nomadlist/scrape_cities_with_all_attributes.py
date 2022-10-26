"""
    LOGIC PROCESS:
        At the end, 'data' will be the list of cities that have all the features present in 'all_features'.

        Next, this list will be exported in a Json file that is used in the process of analyzing the features
        (looking at the feature correlation using a heatmap), step necessary in order to better choose a set of
        3 potential city features lists (features that are not correlated with each other) that might fit for
        the clusterization.
"""

import cloudscraper
import json

from bs4 import BeautifulSoup
from scraping_nomadlist.utils.cities_wanted_features import all_features
from scraping_nomadlist.utils import helper_functions


if __name__ == '__main__':
    data = []

    nomad_page = helper_functions.load_dynamic_page(
        url='https://nomadlist.com/',
        cool_down=3,
        browser_driver_path='../geckodriver.exe'
    )

    # Start working with BeautifulSoup
    soup = BeautifulSoup(nomad_page, 'html.parser')
    city_list = soup.find('ul', {'class': 'grid'})
    cities = city_list.find_all('li', {'data-type': 'city'})[:-1]

    bugged_cities = [
        '{slug}', 'essaouira', 'la-paz-mexico', 'faisalabad',
        'san-jose-costa-rica', 'la-serena', 'cordoba-spain',
        'macau', 'victoria-seychelles', 'george-town-cayman-islands'
    ]

    session = cloudscraper.create_scraper()
    session.max_redirects = 3000

    cities_with_all_features = []
    city_id = 0

    for city in cities:
        curr_city = city['data-slug']
        print(f"City Name: {curr_city}")

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
            keys_with_div_attr_data_value_pattern = {
                'Quality of life score': 'quality_of_life_score',
                'Family score': 'family_score',
                'Fun': 'fun',
                'Education level': 'education_level',
                'English speaking': 'english_speaking',
                'Walkability': 'walkability',
                'Peace no pol conflict': 'peace',
                'Traffic safety': 'traffic_safety',
                'Hospitals': 'hospitals',
                'Healthcare': 'hospitals',
                'Happiness': 'happiness',
                'Nightlife': 'nightlife',
                'Free WiFi in city': 'free_wifi',
                'Places to work from': 'places_to_work',
                'AC or heating': 'ac_heating',
                'Friendly to foreigners': 'friendly_for_foreigners',
                'Freedom of speech': 'freedom_of_speech',
                'Female friendly': 'female_friendly',
                'LGBTQ friendly': 'lgbt_friendly',
                'Startup Score': 'startup_score'
            }
            keys_with_div_attr_class_pattern = {
                'Internet': 'internet',
                'Air quality now': 'air_quality',
                'Safety': 'safety'
            }

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

                if new_key in keys_with_div_attr_class_pattern:
                    feature_name = keys_with_div_attr_class_pattern[new_key]
                    feature_field = r.find('div', {'class': 'rating'})
                    if feature_field:
                        feature_value = int(feature_field['class'][-1][1])
                        curr_city_features[feature_name] = feature_value
                        print(f'{feature_name}: {feature_value}')  # int

                if new_key == 'Total score':
                    feature_name = 'overall_score'
                    overall_score_text = r.find('div', {'class': 'filling'}).find(
                        'span', {'xitemprop': 'ratingValue'}, recursive=False).text
                    if overall_score_text:
                        overall_score_value = float(overall_score_text)
                        curr_city_features[feature_name] = overall_score_value
                        print(f'{feature_name}: {overall_score_value}')  # float

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
            for feature in all_features:
                if feature not in curr_city_features:
                    has_all_features = False
                    break

            print(f'City {curr_city} has all features: {has_all_features}')
            print()
            if has_all_features:
                city_id += 1
                cities_with_all_features.append({'city': curr_city, 'url': city_url})
                data.append({'nr': city_id, 'fields': {}})
                features_dict = data[-1]['fields']

                features_dict['city'] = curr_city
                for feature_name in all_features:
                    features_dict[feature_name] = curr_city_features[feature_name]

    print(f'Cities that have all the attributes: {cities_with_all_features}')
    print(f'Data: {data}')

    with open('files/analyze-data.json', 'w') as outfile:
        json.dump(data, outfile)
