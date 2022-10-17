import json
import math
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def l2_distance(city_1, city_2):
    loss = 0
    for i in range(len(city_1)):
        loss += (city_1[i] - city_2[i]) ** 2

    loss = math.sqrt(loss)
    return loss


test_1_features = [
    'cost',
    'temperature',
    'humidity'
]
test_2_features = [
    'cost',
    'fun',
    'temperature',
    'humidity'
]
test_3_features = [
    'cost',
    'fun',
    'temperature',
    'humidity',
    'walkability'
]

clusters_for_test_1 = True
clusters_for_test_2 = False
clusters_for_test_3 = False

json_for_test_1 = '../Get_Cities_from_Nomadlist_and_Analyze_Them/Files/test_1.json'
json_for_test_2 = '../Get_Cities_from_Nomadlist_and_Analyze_Them/Files/test_2.json'
json_for_test_3 = '../Get_Cities_from_Nomadlist_and_Analyze_Them/Files/test_3.json'

json_add_clusters_for_test_1 = 'Files/fixture_1.json'
json_add_clusters_for_test_2 = 'Files/fixture_2.json'
json_add_clusters_for_test_3 = 'Files/fixture_3.json'

with open(json_for_test_1) as js:
    loaded_json = json.load(js)
    city_names = []
    city_ind = {}  # Dictionary of cities names with its corresponding line in the matrix
    df = pd.DataFrame(columns=test_1_features)

    i = 0

    if clusters_for_test_1 is True:
        num_cols = 3
    elif clusters_for_test_2 is True:
        num_cols = 4
    else:
        num_cols = 5

    for line in loaded_json:
        # print(line)
        pandas_line = []
        curr_city = line['fields']['city']
        curr_dict = line['fields']
        # print(curr_dict)

        if clusters_for_test_1 is True:
            pandas_line.append(curr_dict['cost'])
            pandas_line.append(curr_dict['temperature'])
            pandas_line.append(curr_dict['humidity'])
        elif clusters_for_test_2 is True:
            pandas_line.append(curr_dict['cost'])
            pandas_line.append(curr_dict['fun'])
            pandas_line.append(curr_dict['temperature'])
            pandas_line.append(curr_dict['humidity'])
        else:
            pandas_line.append(curr_dict['cost'])
            pandas_line.append(curr_dict['fun'])
            pandas_line.append(curr_dict['temperature'])
            pandas_line.append(curr_dict['humidity'])
            pandas_line.append(curr_dict['walkability'])

        city_names.append(curr_city)
        city_ind[curr_city] = i  # i = line number in pandas matrix
        df.loc[i] = pandas_line
        i += 1

    print("List of city names: {}".format(city_names))
    print()
    # print(df)

    """ Clustering """
    X = df.values
    X_scaled = MinMaxScaler().fit_transform(X)
    # print(X)
    print(X_scaled)
    # print(len(X))

    """ Min, Max, Mean values for the L2 distance between 2 cities """
    min_val = 100
    max_val = -1
    mean_val = 0

    for i in range(len(X_scaled)):
        for j in range(i + 1, len(X_scaled)):
            first_city = X_scaled[i]
            second_city = X_scaled[j]
            distance = l2_distance(first_city, second_city)

            min_val = min(min_val, distance)
            max_val = max(max_val, distance)
            mean_val += distance

    nr_perechi = (len(X_scaled) * (len(X_scaled) - 1)) / 2
    mean_val /= nr_perechi
    print("Valoarea minima l2: {}, Valoarea maxima l2: {}, Valoarea medie l2: {}".format(min_val, max_val, mean_val))

    mean_cost = sum([city[0] for city in X_scaled]) / len(X_scaled)
    print("Valoarea minima cost: {}, Valoarea maxima cost: {}, Valoarea medie cost: {}".format(0, 1, mean_cost))
    print()

    """ Calculate the best number of clusters """

    ncl_list = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    y_values = []

    best_ncl = -1
    best_score = 0
    for ncl in ncl_list:
        km = KMeans(n_clusters=ncl, random_state=42).fit(X_scaled)
        sil_score = silhouette_score(X_scaled, km.labels_)
        y_values.append(sil_score)
        print("Silhouette score is {} for {} clusters".format(sil_score, ncl))

        if sil_score > best_score:
            best_score = sil_score
            best_ncl = ncl
    print()

    # Plot the silhouette score for each ncl
    x_clusters = ['20', '30', '40', '50', '60', '70', '80', '90', '100', '110', '120']
    plt.bar(x_clusters, y_values, color='#fd7a80', edgecolor='#b10bab')
    plt.xlabel("Numar clustere")
    plt.ylabel("silhouette score")

    plt.show()

    city_clusters = {}
    in_cluster = {}

    print("Best silhouette score is {} for {} clusters".format(best_score, best_ncl))
    print()
    km = KMeans(n_clusters=best_ncl, random_state=42).fit(X_scaled)

    for i in range(len(city_names)):
        curr_cluster = km.labels_[i]
        curr_city = city_names[i]

        if curr_cluster not in city_clusters.keys():
            city_clusters[curr_cluster] = []

        city_clusters[curr_cluster].append(curr_city)
        in_cluster[curr_city] = curr_cluster

    """ List of clusters and their cities """
    clusters = []

    for ind in range(best_ncl):
        clusters.append({"cluster_id": ind, "cities": []})
        print("Cluster {}:".format(ind + 1))

        for i in range(len(city_names)):
            if km.labels_[i] == ind:
                clusters[ind]["cities"].append(city_names[i])
                print(city_names[i])
        print()

    with open("Files/clusters.json", "w") as js_1:
        json.dump(clusters, js_1)

    # Add id_cluster in the Json file for each city
    for dict_temp in loaded_json:
        curr_dict = dict_temp["fields"]
        city_name = curr_dict["city"]

        for cl_dict in clusters:
            if city_name in cl_dict["cities"]:
                dict_temp["fields"]["id_cluster"] = cl_dict["cluster_id"]

    with open(json_add_clusters_for_test_1, 'w') as outfile:
        json.dump(loaded_json, outfile)

    """ Analyze the clusters of some given cities and give recommendations """
    # chosen_cities = ['phuket', 'london', 'florence', 'bangkok', 'dubai', 'paris']
    # cities_to_explore = ['florence']  # The city searched by the user in the form
    # chosen_cities = ['london', 'amsterdam', 'edinburg', 'norwich', 'iasi']  # Cities chose by the user at registration
    # cities_to_explore = ['rome', 'venice', 'naples', 'pisa', 'padova']
    # chosen_cities = ['moscow', 'singapore', 'barcelona', 'madrid', 'amsterdam']
    # cities_to_explore = ['beijing']
    # chosen_cities = ['florence', 'barcelona', 'paris', 'amalfi', 'naples']
    # cities_to_explore = ['lake-como']
    # chosen_cities = ['amalfi', 'edinburgh', 'reykjavik', 'rome', 'london']
    # cities_to_explore = ['oxford']
    # chosen_cities = ['amalfi', 'edinburgh', 'reykjavik', 'oslo', 'london']
    # cities_to_explore = ['stockholm']
    chosen_cities = ['porto', 'ibiza', 'santorini', 'venice', 'mamaia']
    cities_to_explore = ['padova']

    # chosen_cities = ['nice', 'paris', 'toulouse', 'cannes', 'lyon']
    print(chosen_cities)
    print()
    # cities_to_explore = ['nantes']

    for city in cities_to_explore:
        curr_X_city = X_scaled[city_ind[city]]  # Take the characteristics values of the city searched by the user
        curr_cost = curr_X_city[0]
        print("Analysis for {} city:".format(city))
        ind = in_cluster[city]  # The current city's cluster id (current city = city searched by the user)
        print()
        print("{}'s cluster is :".format(city))

        neighbour_cities = city_clusters[ind]
        for neigh in neighbour_cities:
            print(neigh)

        print()

        current_cluster = city_clusters[in_cluster[city]]
        print("Current cluster:", current_cluster)  # All the cities in the current cluster
        print()

        best_score = 100000
        best_city = None
        score_list = []
        for neigh in current_cluster:
            if neigh == city:  # Check if the city from the cluster is the current city
                continue

            score = 0
            neigh_X = X_scaled[city_ind[neigh]]  # Get the current neigh's characteristics's values
            neigh_cost = neigh_X[0]

            for favourite_city in chosen_cities:
                X_city = X_scaled[city_ind[favourite_city]]  # Get the city's characteristics's values
                l2_score = l2_distance(neigh_X, X_city)
                score += l2_score

            # incercam sa minimizam diferenta dintre costul orasului explorat
            # si cel al orasului recomandat pentru a gasi oferte cat mai apropiate
            score += 1.3 * (neigh_cost - curr_cost)

            print("Score for {} is : {}".format(neigh, score))

            score_list.append((neigh, score))

        score_list = sorted(score_list, key=lambda x: x[1])
        print()
        print("Top 3 recommendations are:", score_list[:3])
