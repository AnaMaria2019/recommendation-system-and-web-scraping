"""
    LOGIC PROCESS:
        For the Django application we need to have the features scaled in order to obtain good recommendations.
        In order to quickly access the scaled features of the cities we will have them exported in a separate
        Json file.

        For the Django application we only need the scaled values of the features list that obtained the best
        clustering score (which is represented by 'test-3.json' file), but this script is built for a general
        use, meaning it can be used to export the scaled values for all lists.

    NOTE:
        Replace the list imported from 'cities_wanted_features.py' module with the one for which you want to
        export the scaled values of the cities' features.
"""


import json

from sklearn.preprocessing import MinMaxScaler

from utils import helper_functions
from utils.cities_wanted_features import all_features as city_features


if __name__ == '__main__':
    if len(city_features) == 26:
        data_file_path = '../scraping_nomadlist/files/analyze-data.json'
        output_scaled_data_file_path = 'files/data-with-all-features/scaled-data-all-features.json'
    elif len(city_features) == 5:
        data_file_path = '../scraping_nomadlist/files/test-1.json'
        output_scaled_data_file_path = 'files/test-1/scaled-data-test-1.json'
    elif len(city_features) == 4:
        data_file_path = '../scraping_nomadlist/files/test-2.json'
        output_scaled_data_file_path = 'files/test-2/scaled-data-test-2.json'
    else:
        data_file_path = '../scraping_nomadlist/files/test-3.json'
        output_scaled_data_file_path = 'files/test-3/scaled-data-test-3.json'

    df, city_names, line_index_in_df = helper_functions.read_data_from_json(
        file_path=data_file_path,
        city_features=city_features
    )

    input_data = df.values
    input_data_scaled = MinMaxScaler().fit_transform(input_data)
    scaled_data = []

    for city in city_names:
        idx = line_index_in_df[city]
        curr_line = {'city': city}

        df_column_idx = 0
        for feature_name in city_features:
            field_name = feature_name + '_scaled'
            curr_line[field_name] = input_data_scaled[idx][df_column_idx]
            df_column_idx += 1

        scaled_data.append(curr_line)

    with open(output_scaled_data_file_path, 'w') as outfile:
        json.dump(scaled_data, outfile)
