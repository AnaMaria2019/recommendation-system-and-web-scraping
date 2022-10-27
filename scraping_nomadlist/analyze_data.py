"""
    LOGIC PROCESS:
        The scope of this Python script is to analyze all the features a city from nomadlist.com has, by looking
        at how correlated with one another they are.

        After analyzing all possible features that a city might have, using correlation, 3 potential lists of features
        for a city that enters in the clustering algorithm were chosen.
"""


import seaborn as sns
import matplotlib.pyplot as plt

from scraping_nomadlist.utils.cities_wanted_features import all_features as city_features
from scraping_nomadlist.utils.helper_functions import read_data_from_json


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


if __name__ == '__main__':
    df, cities, _ = read_data_from_json(
        file_path='files/analyze-data.json',
        city_features=city_features
    )
    build_correlation_matrix(dataframe=df)
