import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

with open('Files/analyze_data.json') as js:
    loaded_json = json.load(js)
    city_names = []
    df = pd.DataFrame(columns=[
        'overall_score',
        'nomad_score',
        'quality_of_life_score',
        'family_score',
        'cost',
        'internet',
        'fun',
        'temperature',
        'humidity',
        'air_quality',
        'safety',
        'education_level',
        'english_speaking',
        'walkability',
        'peace',
        'traffic_safety',
        'hospitals',
        'happiness',
        'nightlife',
        'free_wifi',
        'places_to_work',
        'ac_heating',
        'friendly_for_foreigners',
        'freedom_of_speech',
        'racial_tolerance',
        'female_friendly',
        'lgbt_friendly',
        'startup_score'
    ])

    i = 0
    num_cols = 28
    for line in loaded_json:
        # print(line)
        pandas_line = []
        curr_city = line['city']
        curr_dict = line['fields']
        # print(curr_dict)

        if len(curr_dict) < num_cols:
            continue

        pandas_line.append(curr_dict['overall_score'])
        pandas_line.append(curr_dict['nomad_score'])
        pandas_line.append(curr_dict['quality_of_life_score'])
        pandas_line.append(curr_dict['family_score'])
        pandas_line.append(curr_dict['cost'])
        pandas_line.append(curr_dict['internet'])
        pandas_line.append(curr_dict['fun'])
        pandas_line.append(curr_dict['temperature'])
        pandas_line.append(curr_dict['humidity'])
        pandas_line.append(curr_dict['air_quality'])
        pandas_line.append(curr_dict['safety'])
        pandas_line.append(curr_dict['education_level'])
        pandas_line.append(curr_dict['english_speaking'])
        pandas_line.append(curr_dict['walkability'])
        pandas_line.append(curr_dict['peace'])
        pandas_line.append(curr_dict['traffic_safety'])
        pandas_line.append(curr_dict['hospitals'])
        pandas_line.append(curr_dict['happiness'])
        pandas_line.append(curr_dict['nightlife'])
        pandas_line.append(curr_dict['free_wifi'])
        pandas_line.append(curr_dict['places_to_work'])
        pandas_line.append(curr_dict['ac_heating'])
        pandas_line.append(curr_dict['friendly_for_foreigners'])
        pandas_line.append(curr_dict['freedom_of_speech'])
        pandas_line.append(curr_dict['racial_tolerance'])
        pandas_line.append(curr_dict['female_friendly'])
        pandas_line.append(curr_dict['lgbt_friendly'])
        pandas_line.append(curr_dict['startup_score'])

        city_names.append(curr_city)
        df.loc[i] = pandas_line
        i += 1

    print(df)
    df_corr = df.corr(method="pearson")
    print(df_corr)

    # START: Print HeatMap (correlation matrix)
    fig, ax = plt.subplots()
    ax.xaxis.tick_top()
    fig.set_size_inches(13, 8)
    cbar_ax = fig.add_axes([.92, .3, .02, .4])
    sns.set(font_scale=0.7)
    heat_map = sns.heatmap(df_corr, ax=ax, cbar_ax=cbar_ax, xticklabels=df_corr.columns, yticklabels=df_corr.columns,\
                           annot=True)
    heat_map.set_xticklabels(
        heat_map.get_xticklabels(),
        rotation=45,
        horizontalalignment='left'
    )
    plt.show()
    # END

    # Clustering the 532 cities with all the 28 attributes to see how good the result is using all the attributes.
    X = df.values
    X_scaled = MinMaxScaler().fit_transform(X)

    print(X)
    print(X_scaled)
    print(len(X))

    ncl_list = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    best_ncl = -1
    best_score = 0
    for ncl in ncl_list:
        km = KMeans(n_clusters=ncl, random_state=42).fit(X_scaled)
        sil_score = silhouette_score(X_scaled, km.labels_)
        print("Silhouette score is {} for {} clusters".format(sil_score, ncl))
        print()

        if sil_score > best_score:
            best_score = sil_score
            best_ncl = ncl

    city_clusters = {}
    in_cluster = {}

    print("Best silhouette score is {} for {} clusters".format(best_score, best_ncl))  # Not so good!
    km = KMeans(n_clusters=best_ncl, random_state=42).fit(X_scaled)

    for i in range(len(city_names)):
        curr_cluster = km.labels_[i]
        curr_city = city_names[i]

        if curr_cluster not in city_clusters.keys():
            city_clusters[curr_cluster] = []

        city_clusters[curr_cluster].append(curr_city)
        in_cluster[curr_city] = curr_cluster

    clusters = []
    for ind in range(best_ncl):
        clusters.append({"cluster_id": ind, "cities": []})
        # print("Cluster {}:".format(ind + 1))

        for i in range(len(city_names)):
            if km.labels_[i] == ind:
                clusters[ind]["cities"].append(city_names[i])
                # print(city_names[i])
        # print()

    print("Clusters list: {}".format(clusters))

    cities_to_explore = ['phuket', 'london', 'florence', 'bangkok', 'dubai', 'paris']

    for city in cities_to_explore:
        print("Analysis for {} city:".format(city))
        ind = in_cluster[city]
        print()
        print("{}'s cluster is :".format(city))

        neighbour_cities = city_clusters[ind]
        for neigh in neighbour_cities:
            print(neigh)

        print()

    # Print all clusters and their corresponding cities
    ind = 0
    for key in city_clusters:
        ind += 1
        print("Cluster nr.{}:".format(ind))

        city_group = city_clusters[key]
        for city in city_group:
            print(city)
        print()
        print()
