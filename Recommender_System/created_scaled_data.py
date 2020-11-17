import json
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

"""
For the Django application wee need to have the features scaled in order to obtain good recommendations.

After testing clustering on test_1.json, test_2.json and test_3.json, the best clusters were obtained with cities
which have the 3 features (cost, temperature and humidity) and are listed in test_1.json.  
"""

scaled_data = []
with open("../Get_Cities_from_Nomadlist_and_Analyze_Them/Files/test_1.json") as js:
    loaded_json = json.load(js)
    city_names = []
    city_ind = {}  # Dictionary of cities names with its corresponding line in the matrix
    df = pd.DataFrame(columns=['cost', 'temperature', 'humidity'])
    # num_cols = 3
    i = 0

    for line in loaded_json:
        # print(line)
        pandas_line = []
        curr_city = line['fields']['city']
        curr_dict = line['fields']
        # print(curr_dict)

        pandas_line.append(curr_dict['cost'])
        pandas_line.append(curr_dict['temperature'])
        pandas_line.append(curr_dict['humidity'])

        city_names.append(curr_city)
        city_ind[curr_city] = i
        df.loc[i] = pandas_line
        i += 1

    print("List of city names: {}".format(city_names))

    X = df.values
    X_scaled = MinMaxScaler().fit_transform(X)
    print(X_scaled)

    for line in loaded_json:
        ind = city_ind[line['fields']['city']]
        print(ind)
        curr_line = {
            'city': line['fields']['city'],
            'cost_scaled': X_scaled[ind][0],
            'temperature_scaled': X_scaled[ind][1],
            'humidity_scaled': X_scaled[ind][2]
        }
        print(curr_line)
        scaled_data.append(curr_line)

with open('Files/scaled_data.json', 'w') as outfile:
    json.dump(scaled_data, outfile)
