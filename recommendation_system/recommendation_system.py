import json
import math
import pandas as pd

from utils.cities_wanted_features import selected_cities_features_3 as city_features


def read_scaled_data_from_json(file_path, features_names):
    scaled_features_names = [name + '_scaled' for name in features_names]
    df = pd.DataFrame(columns=scaled_features_names)
    line_index_in_dataframe = {}

    with open(file_path) as input_file:
        loaded_json = json.load(input_file)

        pandas_idx = 0
        for line in loaded_json:
            pandas_line = []
            current_city_name = line['city']

            for feature in scaled_features_names:
                pandas_line.append(line[feature])

            df.loc[pandas_idx] = pandas_line
            line_index_in_dataframe[current_city_name] = pandas_idx
            pandas_idx += 1

    return df, line_index_in_dataframe


def get_clustering_information(file_clusters_path, file_cities_info_path):
    clusters_info = {}
    city_in_cluster = {}

    with open(file_clusters_path) as clusters_file:
        loaded_json = json.load(clusters_file)

        for line in loaded_json:
            cluster_id = line['cluster_id']
            cluster_cities = line['cities']

            clusters_info[cluster_id] = cluster_cities

    with open(file_cities_info_path) as cities_info:
        loaded_json = json.load(cities_info)

        for line in loaded_json:
            current_dict = line['fields']
            current_city_name = current_dict['city']
            current_city_cluster_id = current_dict['id_cluster']

            city_in_cluster[current_city_name] = current_city_cluster_id

    return clusters_info, city_in_cluster


def l2_distance(city_1, city_2):
    loss = 0
    for idx in range(len(city_1)):
        loss += (city_1[idx] - city_2[idx]) ** 2

    loss = math.sqrt(loss)
    return loss


def get_min_max_and_mean_values_for_l2_distance(cities_info_scaled_values):
    """ Min, Max, Mean values for the L2 distance between any 2 cities """
    min_val = 100
    max_val = -1
    mean_val = 0
    nr_cities = len(cities_info_scaled_values)

    for i in range(nr_cities):
        for j in range(i + 1, nr_cities):
            first_city = cities_info_scaled_values[i]
            second_city = cities_info_scaled_values[j]
            distance = l2_distance(first_city, second_city)

            min_val = min(min_val, distance)
            max_val = max(max_val, distance)
            mean_val += distance

    nr_unique_pairs = (nr_cities * (nr_cities - 1)) / 2
    mean_val /= nr_unique_pairs

    return min_val, max_val, mean_val


def get_recommendations(
        df_cities_info, line_idx_in_df, city_in_cluster, all_clusters,
        user_favorite_cities, user_destination_city
):
    print(f'Analysis for {user_destination_city} city:')
    # Take the scaled features values of the city searched by the user
    destination_info = df_cities_info[line_idx_in_df[user_destination_city]]
    destination_cost = destination_info[0]
    # The user's destination city cluster id (city searched by the user in the application PennyTravel)
    cluster_id = city_in_cluster[user_destination_city]
    print(f"{user_destination_city}'s cluster is :")

    destination_cluster_neighbour_cities = all_clusters[cluster_id]
    for city in destination_cluster_neighbour_cities:
        print(city)
    print()

    score_list = []
    for city in destination_cluster_neighbour_cities:
        # NOTE: There is no point in considering the user's destination city itself as a possible
        #       recommendation
        if city == user_destination_city:
            continue

        score = 0
        # Get the current neigh's characteristics' values
        current_neigh_info = df_cities_info[line_idx_in_df[city]]
        current_neigh_cost = current_neigh_info[0]

        # The user chooses a few favorite cities at the registration step
        # in the application PennyTravel
        for favourite_city in user_favorite_cities:
            # Get the favorite city's characteristics' values
            current_favorite_info = df_cities_info[line_idx_in_df[favourite_city]]
            # Calculate the distance between the current destination's neighbour city
            # and the current user's favorite city
            l2_score = l2_distance(current_neigh_info, current_favorite_info)
            score += l2_score

        # We are trying to minimize the cost difference between the user's destination city
        # and the possible recommended city from its cluster, in order to get more similar offers
        score += 1.3 * (current_neigh_cost - destination_cost)
        print(f'Score for {city} is : {score}')

        score_list.append((city, score))

    score_list = sorted(score_list, key=lambda x: x[1])
    top_3_recommendations = score_list[:3]

    return top_3_recommendations


if __name__ == '__main__':
    if len(city_features) == 5:
        input_file_path = 'files/test-1/scaled-data-test-1.json'
        input_clusters_file_path = 'files/test-1/clusters-test-1.json'
        input_cities_info_file_path = 'files/test-1/fixture-test-1.json'
    elif len(city_features) == 4:
        input_file_path = 'files/test-2/scaled-data-test-2.json'
        input_clusters_file_path = 'files/test-2/clusters-test-2.json'
        input_cities_info_file_path = 'files/test-2/fixture-test-2.json'
    else:
        input_file_path = 'files/test-3/scaled-data-test-3.json'
        input_clusters_file_path = 'files/test-3/clusters-test-3.json'
        input_cities_info_file_path = 'files/test-3/fixture-test-3.json'

    scaled_df, line_index_in_df = read_scaled_data_from_json(
        file_path=input_file_path,
        features_names=city_features
    )

    scaled_values = scaled_df.values
    total_nr_cities = len(scaled_values)

    clusters, in_cluster = get_clustering_information(
        file_clusters_path=input_clusters_file_path,
        file_cities_info_path=input_cities_info_file_path
    )

    l2_min, l2_max, l2_mean = get_min_max_and_mean_values_for_l2_distance(
        cities_info_scaled_values=scaled_values
    )
    print(f'l2 distance min value: {l2_min}')
    print(f'l2 distance max value: {l2_max}')
    print(f'l2 distance mean value: {l2_mean}')
    print()

    mean_cost = sum([city_scaled_values[0] for city_scaled_values in scaled_values]) / total_nr_cities
    print(f'Mean scaled value for cost feature: {mean_cost}')
    print()

    """ Analyze the clusters of a given destination city and give 3 recommendations """
    favorite_cities = ['london', 'amsterdam', 'edinburg', 'norwich', 'iasi']
    # The city searched by the user in the PennyTravel's application form
    destination_city = 'rome'

    recommended_cities = get_recommendations(
        df_cities_info=scaled_values,
        line_idx_in_df=line_index_in_df,
        city_in_cluster=in_cluster,
        all_clusters=clusters,
        user_favorite_cities=favorite_cities,
        user_destination_city=destination_city
    )
    print(f"User's favorite cities: {favorite_cities}")
    print(f"User's destination city: {destination_city}")
    print(f"Top 3 recommendations: {recommended_cities}")
