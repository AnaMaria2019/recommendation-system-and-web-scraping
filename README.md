# RecSystem_and_WebScraping

pip install -r Requirements.txt

### Logic steps:

1) Get all the cities from [nomadlist.com](https://nomadlist.com/) where <b>each city</b> has have <b>27 attributes</b> and save them in a Json file
2) Analyze these cities (532 cities)
3) Create 3 Json files for the 3 potential lists of good cities attributes for K-Means clustering
4) Perfom K-Means Clustering on these 3 Json files and keep the best version (with the best clusterization: test_1.json) and create the <b>final_fixture.json</b> file used for populating the application's database for TravelApp project
5) Add to the final_fixture.json file airport_code and image to each city (1330 cities)
