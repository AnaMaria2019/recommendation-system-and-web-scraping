# recommendation-system-and-web-scraping

## Logic steps followed - building the Recommendation System:
> **Note**
> Below each step, the associated script in this repository is mentioned.</br>

> **Note**
> For each list of characteristics (mentioned [here](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/utils/cities_wanted_features.py)), the number of cities, that have those characteristics, along with the characteristics' values, found on [nomadlist.com](https://nomadlist.com/) might fluctuate because the website is constantly updating its information.

1) Get all the cities from [nomadlist.com](https://nomadlist.com/) that have the <b>26 attributes</b> (you can find them in <i>[utils/cities_wanted_features.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/utils/cities_wanted_features.py)</i>) selected from the full list of 35 possible ones, and store them in a Json file</br>
-- <i>[scraping_nomadlist/scrape_cities_with_all_attributes.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/scraping_nomadlist/scrape_cities_with_all_attributes.py)</i> -- 
2) Analyze these cities - <i>917</i> cities found with all 26 attributes - <b>heatmap visualization</b> of the <b>attributes correlation</b></br>
-- <i>[scraping_nomadlist/analyze_data.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/scraping_nomadlist/analyze_data.py)</i> --
3) Remove considered redundant attributes for a recommendation system designed to be integrated within a travel application and create 3 Json files for the 3 potential lists of good cities' attributes for K-Means clustering algorithm (<i>test-1.json</i> - contains <i>1333</i> cities, <i>test-2.json</i> - contains <i>1334</i> cities, <i>test-3.json</i> - contains <i>1339</i> cities)</br>
-- <i>[scraping_nomadlist/scrape_cities_with_variable_nr_attributes.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/scraping_nomadlist/scrape_cities_with_variable_nr_attributes.py)</i> --
4) Perfom K-Means Clustering on these 3 Json files and store the results in Json files</br>
-- <i>[recommendation_system/kmeans_clustering.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/recommendation_system/kmeans_clustering.py)</i> --
5) Store the scaled values of the cities' characteristics in a separate Json file for each list of attributes files (stored in test-1.json, test-2.json, test-3.json and analyze-data.json) - the scaled values are needed for the recommendation algorithm.</br>
NOTE: In the TravelApp application only the scaled values of the cities' characteristics, from the list that obtained the best clusterization, will be needed, but for experimental reasons, in this repository the recommendation algorithm can be tested on all lists of cities' characteristics</br>
-- <i>[recommendation_system/export_scaled_data.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/recommendation_system/export_scaled_data.py)</i> --
6) Build and apply the recommendation system that will be integrated in the TravelApp application</br>
-- <i>[recommendation_system/recommendation_system.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/recommendation_system/recommendation_system.py)</i> --
7) Keep the list of cities' attributes that obtained the best shillouette score in the clusterization process (with the best clusterization: fixture-test-3.json) and add an <b>airport_code</b> and an <b>image</b> to each city (1339 total cities) (the airport code and the image will be later needed in the TravelApp) then create the <b>final-fixture.json</b> file that will be used later for populating the application's database in the TravelApp project</br>
-- <i>[scrape_airportcode_and_create_final_fixture.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/scrape_airportcode_and_create_final_fixture.py)</i> --

## Web scraping techniques for searching accommodation and flight
The logic developed in the following scripts will be later used in the process of building the TravelApp project

1) Finding accommodation for a given destination in a period of time for a number of persons and rooms</br>
-- <i>[scraping_accommodation_and_flight/scrape_accommodation_on_booking.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/scraping_accommodation_and_flight/scrape_accommodation_on_booking.py)</i> --
2) Finding best flight option for a given destination in a period of time</br>
-- <i>[scraping_accommodation_and_flight/scrape_flight_on_momondo.py](https://github.com/AnaMaria2019/recommendation-system-and-web-scraping/blob/master/scraping_accommodation_and_flight/scrape_flight_on_momondo.py)</i> --


## Getting started

### Prerequisites

* [Python 3.8.0](https://www.python.org/downloads/release/python-380/)
* [Git](https://git-scm.com/downloads)

### Setup steps (on Windows operating system)

1. Open cmd
2. Go to the directory you want to clone this repository using <i>cd</i> command
3. Clone this GitHub repository on your computer by using either SSH or HTTPS option:</br>
`git clone git@github.com:AnaMaria2019/recommendation-system-and-web-scraping.git` (SSH)
4. Change directory to the directory just cloned, <i>RecSystem_and_WebScraping</i>
5. Create a python virtual environment and activate it:</br>
`python -m venv <name_of_the_venv>`</br>
`<name_of_the_venv>\Scripts\activate` - this works only for Windows
6. Install the necessary packages mentioned in the <i>requirements.txt</i> file:</br>
`pip install -r requirements.txt`
