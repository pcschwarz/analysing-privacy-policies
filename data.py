import pandas as pd

def get_data(selected_genres, selected_countries, selected_range):
    """
    Returns the data that is contained in the final_dataframe.json file.
    :return: DataFrame that contains the data.
    """

    df = pd.read_json("data/final_dataframe.json")
    # only selected genres get returned
    df = df[df['genre'].isin(selected_genres)]
    # only selected countries get returned
    df = df[df['hostingLocation'].isin(selected_countries)]
    # only privacy policies inside the selected maxInstalls range get returned
    df = df[df['maxInstalls'] > selected_range[0]]
    if selected_range[1] < 10000000:
        df = df[df['maxInstalls'] < selected_range[1]]
    df.reset_index(inplace=True, drop=True)
    return df


def get_available_genres():
    df = pd.read_json("data/final_dataframe.json")
    return df["genre"].unique()


def get_available_genres_label_value_pairs():
    result = []
    available_genres = get_available_genres()
    for genre in available_genres:
        result.append({'label': genre, 'value': genre})
    return result


def get_available_countries():
    df = pd.read_json("data/final_dataframe.json")
    return df["hostingLocation"].unique()


def get_available_countries_label_value_pairs():
    result = []
    available_countries = get_available_countries()
    for country in available_countries:
        result.append({'label': country, 'value': country})
    return result

def get_ranked_dataframe(grouping_var, ranking_var):
    df = pd.read_json("data/final_dataframe.json")
    group_series = df[grouping_var]
    rank_series = df[ranking_var].rank(ascending=True)
    ranked_dataframe = group_series.to_frame().join(rank_series)
    ranked_dataframe = ranked_dataframe.groupby([grouping_var]).mean()
    return ranked_dataframe

def get_mean_rank(ranked_dataframe, ranking_var, grouping_var_value):
    if grouping_var_value == "Country":
        return None
    return ranked_dataframe.at[grouping_var_value, ranking_var].round(1)
