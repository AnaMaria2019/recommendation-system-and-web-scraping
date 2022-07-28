# RecSystem_and_WebScraping

pip install -r Requirements.txt

### Logic steps:

1) Get all the cities from [nomadlist.com](https://nomadlist.com/) where <b>each city</b> has have <b>28 attributes</b> and save them in a Json file
2) Analyze these cities - only 532 cities found with all 28 attributes - <b>heatmap visualization</b> of the <b>attributes correlation</b>  
3) Remove considered redundant attributes for a recommendation system designed to be integrated within a travel application and create 3 Json files for the 3 potential lists of good cities' attributes for K-Means clustering algorithm
4) Perfom K-Means Clustering on these 3 Json files and keep the best version (with the best clusterization: test_1.json) and create the <b>final_fixture.json</b> file used for populating the application's database for TravelApp project
5) <b>Add</b> to the final_fixture.json file <b>airport_code</b> and <b>image</b> to each city (1330 total cities that have the previously chosen attributes) - the airport code and the image will be later needed in the TravelApp
