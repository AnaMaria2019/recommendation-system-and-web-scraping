"""
    LOGIC PROCESS:
        The scope of this Python script is to apply KMeans Clustering on each combination of features (chosen
        in the process of analyzing all the features a city on nomadlist.com can have) and evaluate what set of
        features obtains the best score.

        The data is stored in 'test-1.json', 'test-2.json', 'test-3.json' for the 3 lists chosen at the analyzing
        step of the process. We also included testing KMeans Clustering on all features set, the cities with all
        features being stored in 'analyze-data.json'.

    NOTE:
        Replace the list imported from 'cities_wanted_features.py' module with the one for which you want to test
        KMeans Clustering.
"""


import json
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from scraping_nomadlist.utils.cities_wanted_features import selected_cities_features_3 as city_features
from scraping_nomadlist.utils.helper_functions import read_data_from_json


def find_best_nr_of_clusters(X, nr_clusters_to_be_tested):
    y_values = []

    best_ncl = -1
    best_score = 0
    for ncl in nr_clusters_to_be_tested:
        km = KMeans(n_clusters=ncl, random_state=42).fit(X)
        sil_score = silhouette_score(X, km.labels_)
        y_values.append(sil_score)
        print(f'Silhouette score is {sil_score} for {ncl} clusters')

        if sil_score > best_score:
            best_score = sil_score
            best_ncl = ncl

    return best_ncl, best_score, y_values


def plot_clustering_results(nr_clusters, y_values):
    # Plot the silhouette score for each nr of clusters
    x_clusters = [str(nr) for nr in nr_clusters]

    plt.bar(x_clusters, y_values, color='#fd7a80', edgecolor='#b10bab')
    plt.xlabel("Number of clusters")
    plt.ylabel("silhouette score")
    plt.show()


def build_clustering(X, nr_clusters_to_be_tested, cities_name):
    best_nr_clusters, best_score, y_values = find_best_nr_of_clusters(
        X=X,
        nr_clusters_to_be_tested=nr_clusters_to_be_tested
    )

    # Plot clustering results
    plot_clustering_results(
        nr_clusters=nr_clusters_to_be_tested,
        y_values=y_values
    )

    print(f'Best silhouette score is {best_score} for {best_nr_clusters} clusters')
    # When clustering the cities based all of their features,
    # best silhouette score is 0.13796554112515688 for 20 clusters - Not so good!

    km = KMeans(n_clusters=best_nr_clusters, random_state=42).fit(X)

    # {cluster_id: list of cities that are part of the cluster with id == cluster_id}
    cities_clusters = {}
    # {city_name: corresponding cluster_id}
    in_cluster = {}

    for i in range(len(cities_name)):
        cluster = km.labels_[i]
        current_city = cities_name[i]

        if cluster not in cities_clusters.keys():
            cities_clusters[cluster] = []

        cities_clusters[cluster].append(current_city)
        in_cluster[current_city] = cluster

    return cities_clusters, in_cluster


def export_clusters(output_file_path, cities_clusters):
    clusters_l = []
    for ind in range(len(cities_clusters)):
        clusters_l.append({'cluster_id': ind, 'cities': []})

        cities_group = cities_clusters[ind]
        for city in cities_group:
            clusters_l[ind]['cities'].append(city)

    with open(output_file_path, 'w') as js:
        json.dump(clusters_l, js)

    return clusters_l


def export_given_cities_clusters(output_file_path, cities_to_be_explored, cities_clusters, in_cluster):
    with open(output_file_path, 'w') as output_obj:
        for city in cities_to_be_explored:
            output_obj.write(f'Analysis for {city} city:\n')
            cluster_idx = in_cluster[city]
            output_obj.write(f"{city}'s cluster contains the following cities:\n")

            neighbour_cities = cities_clusters[cluster_idx]
            for neigh in neighbour_cities:
                output_obj.write(neigh + '\n')

            output_obj.write('\n')


def insert_cluster_id_to_cities_files(file_path, output_file_path, clusters_l):
    with open(file_path) as js:
        loaded_json = json.load(js)

        for dictionary in loaded_json:
            curr_dict = dictionary['fields']
            city_name = curr_dict['city']

            for cluster_dict in clusters_l:
                if city_name in cluster_dict['cities']:
                    dictionary['fields']['id_cluster'] = cluster_dict['cluster_id']

        with open(output_file_path, 'w') as outfile:
            json.dump(loaded_json, outfile)


if __name__ == '__main__':
    output_fixture_file_path = None

    if len(city_features) == 26:
        # We tested KMeans Clustering Algorithm on the 917 cities with all features
        # to see how good the result is when using all features too.
        data_file_path = '../scraping_nomadlist/files/analyze-data.json'
        output_clusters_file_path = 'files/data-with-all-features/clusters-all-features.json'
        output_explored_cities_file_path = 'files/data-with-all-features/explored-cities-for-all-features-data.txt'
    elif len(city_features) == 5:
        data_file_path = '../scraping_nomadlist/files/test-1.json'
        output_clusters_file_path = 'files/test-1/clusters-test-1.json'
        output_fixture_file_path = 'files/test-1/fixture-test-1.json'
        output_explored_cities_file_path = 'files/test-1/explored-cities-for-test-1.txt'
    elif len(city_features) == 4:
        data_file_path = '../scraping_nomadlist/files/test-2.json'
        output_clusters_file_path = 'files/test-2/clusters-test-2.json'
        output_fixture_file_path = 'files/test-2/fixture-test-2.json'
        output_explored_cities_file_path = 'files/test-2/explored-cities-for-test-2.txt'
    else:
        data_file_path = '../scraping_nomadlist/files/test-3.json'
        output_clusters_file_path = 'files/test-3/clusters-test-3.json'
        output_fixture_file_path = 'files/test-3/fixture-test-3.json'
        output_explored_cities_file_path = 'files/test-3/explored-cities-for-test-3.txt'

    df, city_names, line_index_in_df = read_data_from_json(
        file_path=data_file_path,
        city_features=city_features
    )

    """ Clustering """
    input_data = df.values
    input_data_scaled = MinMaxScaler().fit_transform(input_data)
    print(f'Input data: {input_data}')
    print(f'Input data length: {len(input_data)}')
    print(f'Scaled input data: {input_data_scaled}')
    ncl_list = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]

    clusters, city_in_cluster = build_clustering(
        X=input_data_scaled,
        nr_clusters_to_be_tested=ncl_list,
        cities_name=city_names
    )

    """ List of clusters and their cities """
    clusters_list = export_clusters(
        output_file_path=output_clusters_file_path,
        cities_clusters=clusters
    )

    # Looking at some cities' cluster to see if the other cities in their
    # corresponding cluster are similar to them (checking how accurate the clustering is)
    cities_to_explore = ['phuket', 'london', 'florence', 'bangkok', 'dubai', 'paris']
    export_given_cities_clusters(
        output_file_path=output_explored_cities_file_path,
        cities_to_be_explored=cities_to_explore,
        cities_clusters=clusters,
        in_cluster=city_in_cluster
    )

    if output_fixture_file_path:
        """ Insert id_cluster for each city in the Json file """
        insert_cluster_id_to_cities_files(
            file_path=data_file_path,
            output_file_path=output_fixture_file_path,
            clusters_l=clusters_list
        )
