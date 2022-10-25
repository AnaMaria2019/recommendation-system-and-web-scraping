import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scraping_nomadlist.utils.cities_wanted_features import all_features as city_features


def read_data(file_path):
    with open(file_path) as js:
        loaded_json = json.load(js)
        cities = []
        dataframe = pd.DataFrame(columns=city_features)

        pandas_index = 0
        num_cols = len(city_features)
        for line in loaded_json:
            pandas_line = []
            current_city = line['city']
            curr_dict = line['fields']

            if len(curr_dict) < num_cols:
                continue

            for feature_name in city_features:
                pandas_line.append(curr_dict[feature_name])

            cities.append(current_city)
            dataframe.loc[pandas_index] = pandas_line
            pandas_index += 1

        return dataframe, cities


def build_correlation_matrix(dataframe):
    df_correlation = dataframe.corr(method="pearson")

    # START: Print HeatMap (correlation matrix)
    fig, ax = plt.subplots()
    ax.xaxis.tick_top()
    fig.set_size_inches(13, 8)
    cbar_ax = fig.add_axes([.92, .3, .02, .4])
    sns.set(font_scale=0.7)
    heat_map = sns.heatmap(
        df_correlation,
        ax=ax,
        cbar_ax=cbar_ax,
        xticklabels=df_correlation.columns,
        yticklabels=df_correlation.columns,
        annot=True
    )
    heat_map.set_xticklabels(
        heat_map.get_xticklabels(),
        rotation=45,
        horizontalalignment='left'
    )
    plt.show()
    # END


def find_best_nr_of_clusters(X, nr_clusters_to_be_tested):
    best_ncl = -1
    best_score = 0
    for ncl in nr_clusters_to_be_tested:
        km = KMeans(n_clusters=ncl, random_state=42).fit(X)
        sil_score = silhouette_score(X, km.labels_)
        print(f'Silhouette score is {sil_score} for {ncl} clusters')

        if sil_score > best_score:
            best_score = sil_score
            best_ncl = ncl

    return best_ncl, best_score


def build_clustering(X, nr_clusters_to_be_tested):
    X_scaled = MinMaxScaler().fit_transform(X)
    print(f'Input data: {X}')
    print(f'Input data length: {len(X)}')
    print(f'Scaled input data: {X_scaled}')

    best_nr_clusters, best_score = find_best_nr_of_clusters(
        X=X_scaled,
        nr_clusters_to_be_tested=nr_clusters_to_be_tested
    )
    print(f'Best silhouette score is {best_score} for {best_nr_clusters} clusters')  # Not so good!
    # Best silhouette score is 0.1363683821883101 for 20 clusters

    km = KMeans(n_clusters=best_nr_clusters, random_state=42).fit(X_scaled)

    # {cluster_id: list of cities that are part of the cluster with id == cluster_id}
    cities_clusters = {}
    # {city_name: corresponding cluster_id}
    in_cluster = {}

    for i in range(len(city_names)):
        cluster = km.labels_[i]
        current_city = city_names[i]

        if cluster not in cities_clusters.keys():
            cities_clusters[cluster] = []

        cities_clusters[cluster].append(current_city)
        in_cluster[current_city] = cluster

    return cities_clusters, in_cluster


def export_clusters(output_file_path, clusters):
    with open(output_file_path, 'w') as output_obj:
        for cluster_id in (range(len(clusters))):
            output_obj.write(f'Cluster {cluster_id}:\n')

            cities_group = clusters[cluster_id]
            for city in cities_group:
                output_obj.write(city + '\n')

            output_obj.write('\n\n')


def export_cities_clusters(output_file_path, cities_to_explore, clusters, in_cluster):
    with open(output_file_path, 'w') as output_obj:
        for city in cities_to_explore:
            output_obj.write(f'Analysis for {city} city:\n')
            cluster_idx = in_cluster[city]
            output_obj.write(f"{city}'s cluster contains the following cities:\n")

            neighbour_cities = clusters[cluster_idx]
            for neigh in neighbour_cities:
                output_obj.write(neigh + '\n')

            output_obj.write('\n')


if __name__ == '__main__':
    df, city_names = read_data(file_path='files/analyze_data.json')
    build_correlation_matrix(dataframe=df)

    # Clustering the 532 cities with all the 28 attributes to see how good the result is using all the attributes.
    input_data = df.values
    ncl_list = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    city_cluster, city_in_cluster = build_clustering(X=input_data, nr_clusters_to_be_tested=ncl_list)

    # Looking at some cities' cluster to see if the other cities in their
    # corresponding cluster are similar to them (checking how accurate the clustering is)
    cities_to_explore = ['phuket', 'london', 'florence', 'bangkok', 'dubai', 'paris']
    export_cities_clusters(
        output_file_path='files/explorred_cities.txt',
        cities_to_explore=cities_to_explore,
        clusters=city_cluster,
        in_cluster=city_in_cluster
    )

    # Write all clusters and their corresponding cities in a text file
    export_clusters(output_file_path='files/clusters.txt', clusters=city_cluster)
