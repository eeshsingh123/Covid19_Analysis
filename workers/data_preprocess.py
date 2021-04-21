import pandas as pd
import numpy as np

from config import PATHS


keep_cols = [
            'Updated On', 'State', 'Total Individuals Registered', 'First Dose Administered',
            'Second Dose Administered', 'Male(Individuals Vaccinated)', 'Female(Individuals Vaccinated)',
            'Transgender(Individuals Vaccinated)', 'Total Covaxin Administered', 'Total CoviShield Administered',
            'Total Doses Administered'
        ]


class GraphDataFormatter:

    def __init__(self, path=PATHS):
        self.path = path
        # Daily active, confirmed, death cases
        self.time_series_df = pd.read_csv(self.path['time_series_df'])

        # State wise Total data, Also includes total cases for the current day in the top row
        self.state_wise_total_df = pd.read_csv(self.path['states']['state_total'])
        self.state_wise_total_df.drop('State_Notes', axis=1, inplace=True)
        # State wise daily data
        self.state_wise_daily_df = pd.read_csv(self.path['states']['state_daily'])
        self.state_wise_daily_df.fillna(0.0, axis=1, inplace=True)

        # District wise total data
        self.district_wise_total_df = pd.read_csv(self.path['districts']['district_total'])
        self.district_wise_total_df.drop('District_Notes', axis=1, inplace=True)
        # District wise daily data
        self.district_wise_daily_df = pd.read_csv(self.path['districts']['district_daily'])
        self.district_wise_daily_df.fillna(0.0, axis=1, inplace=True)

        # Vaccination data
        self.vaccine_state_df = pd.read_csv(self.path['vaccination']['state_daily'])
        self.vaccine_state_df = self.vaccine_state_df[keep_cols]
        self.vaccine_state_df.rename(columns={
            'Male(Individuals Vaccinated)': 'Male', 'Female(Individuals Vaccinated)': 'Female',
            'Transgender(Individuals Vaccinated)': 'Transgender'
        }, inplace=True)
        self.vaccine_state_df.fillna(0.0, axis=1, inplace=True)

        self.vaccine_state_total_df = pd.read_csv(self.path['vaccination']['state_total'])

        print("All Dataframes Loaded Successfully!")

    def get_current_days_data(self):
        current_stats = dict(self.state_wise_total_df.iloc[0])
        current_vaccine_administered = list(self.vaccine_state_total_df.iloc[-1])[-1]
        current_stats.update({"Vaccine Administered": current_vaccine_administered})
        return {
            "state": "Total",
            "data": [current_stats]
        }

    def get_time_series_data(self):
        total_cases_df = self.time_series_df[['Date', 'Date_YMD', 'Total Confirmed', 'Total Recovered', 'Total Deceased']]
        daily_cases_df = self.time_series_df[['Date', 'Date_YMD', 'Daily Confirmed', 'Daily Recovered', 'Daily Deceased']]

        total = {
            "state": "Total",
            "data": [
                {
                    'name': f'Total {d_type}',
                    'x': list(total_cases_df['Date_YMD']),
                    'y': list(total_cases_df[f'Total {d_type}'])
                }
                for d_type in ['Confirmed', 'Recovered', 'Deceased']
            ]
        }
        daily = {
            "state": "Total",
            "data": [
                {
                    'name': f'Daily {d_type}',
                    'x': list(daily_cases_df['Date_YMD']),
                    'y': list(daily_cases_df[f'Daily {d_type}'])
                }
                for d_type in ['Confirmed', 'Recovered', 'Deceased']
            ]
        }
        del total_cases_df, daily_cases_df
        return total, daily

    def get_state_wise_data(self, state):
        daily_state_df = self.state_wise_daily_df[self.state_wise_daily_df['State'] == state]
        total_state_df = self.state_wise_total_df[self.state_wise_total_df['State'] == state].to_dict()
        daily = {
            "state": state,
            "data": [
                {
                    "name": d_type,
                    "x": list(daily_state_df['Date']),
                    "y": list(daily_state_df[d_type])
                }
                for d_type in ['Confirmed', 'Recovered', 'Deceased', 'Tested']
            ]
        }
        total = {
            "state": state,
            "data": [
                {
                    column: col_val for column, col_dict in total_state_df.items() for idx, col_val in col_dict.items()
                    if
                    column != 'State'
                }
            ]
        }
        del daily_state_df, total_state_df
        return total, daily

    def get_district_data(self, state, district):
        district_daily_df = self.district_wise_daily_df[
            (self.district_wise_daily_df['State'] == state) & (self.district_wise_daily_df['District'] == district)
        ]
        district_total_df = self.district_wise_total_df[
            (self.district_wise_total_df['State'] == state) & (self.district_wise_total_df['District'] == district)
        ].to_dict()

        daily = {
            "state": state,
            "district": district,
            "data": [
                {
                    column: col_val for column, col_dict in district_total_df.items() for idx, col_val in col_dict.items()
                    if
                    column not in ["State", "District_Key", "District"]
                }
            ]
        }

        total = {
            "state": state,
            "district": district,
            "data": [
                {
                    "name": d_type,
                    "x": list(district_daily_df['Date']),
                    "y": list(district_daily_df[d_type])
                }
                for d_type in ['Confirmed', 'Recovered', 'Deceased', 'Tested']
            ]
        }
        del district_daily_df, district_total_df
        return total, daily

    def get_vaccine_data(self, state):

        vac_dict = self.vaccine_state_df[self.vaccine_state_df["State"] == state].to_dict()
        vac_data = {col_name: list(col_val.values()) for col_name, col_val in vac_dict.items()}

        vac_total_data = dict(self.vaccine_state_total_df[self.vaccine_state_total_df['State'] == state].iloc[0])

        daily = {
            "state": state,
            "data": vac_data
        }
        total = {
            "state": state,
            "data": [{
                "state": vac_total_data.pop('State'),
                "x": list(vac_total_data.keys()),
                "y": list(vac_total_data.values()),
            }]
        }
        del vac_data, vac_total_data
        return total, daily


if __name__ == "__main__":
    gdf = GraphDataFormatter()
    tot, dly = gdf.get_state_wise_data(state="Maharashtra")
    print("TOTAL DATA--------->")
    print(tot)
    print("="*39)
    print("DAILY DATA--------->")
    print(dly)


