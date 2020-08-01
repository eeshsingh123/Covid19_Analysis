from functools import reduce

import pandas as pd
from config import BASE_PATH

xx = pd.read_csv(f"{BASE_PATH}\\twitter_db\\kaggle_data\\time_series_covid_19_confirmed.csv")
yy = pd.read_csv(f"{BASE_PATH}\\twitter_db\\kaggle_data\\time_series_covid_19_deaths.csv")
zz = pd.read_csv(f"{BASE_PATH}\\twitter_db\\kaggle_data\\time_series_covid_19_recovered.csv")


def prepare_df(country):

    if country == "Mainland China":
        country = "China"

    if country == "UK":
        country = "United Kingdom"

    x1 = xx.drop(['Province/State', 'Lat', 'Long'], axis=1)
    y1 = yy.drop(['Province/State', 'Lat', 'Long'], axis=1)
    z1 = zz.drop(['Province/State', 'Lat', 'Long'], axis=1)

    dff1 = x1.groupby(['Country/Region']).sum()
    dff2 = y1.groupby(['Country/Region']).sum()
    dff3 = z1.groupby(['Country/Region']).sum()

    dff1.reset_index(inplace=True)
    dff2.reset_index(inplace=True)
    dff3.reset_index(inplace=True)

    samp1 = dff1[dff1["Country/Region"] == country].T
    samp2 = dff2[dff2["Country/Region"] == country].T
    samp3 = dff3[dff3["Country/Region"] == country].T

    samp1.reset_index(inplace=True)
    samp2.reset_index(inplace=True)
    samp3.reset_index(inplace=True)

    samp1.columns = ['Date', 'Confirmed']
    samp2.columns = ['Date', 'Deaths']
    samp3.columns = ['Date', 'Recovered']

    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['Date']), [samp1, samp2, samp3])
    df_merged = df_merged[4:]
    df_merged.dropna(axis=0, inplace=True)

    df_merged['Confirmed'] = df_merged['Confirmed'].astype('int')
    df_merged['Deaths'] = df_merged['Deaths'].astype('int')
    df_merged['Recovered'] = df_merged['Recovered'].astype('int')

    diff_df = df_merged.set_index('Date').diff().reset_index()

    diff_df.dropna(axis=0, inplace=True)

    return diff_df


if __name__ == "__main__":
    prepare_df("China")