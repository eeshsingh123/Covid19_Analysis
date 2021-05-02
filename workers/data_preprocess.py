import pandas as pd
import numpy as np

from config import PATHS, COLOR_LIST


keep_cols = [
            'Updated On', 'State', 'Total Individuals Registered', 'First Dose Administered',
            'Second Dose Administered', 'Male(Individuals Vaccinated)', 'Female(Individuals Vaccinated)',
            'Transgender(Individuals Vaccinated)', 'Total Covaxin Administered', 'Total CoviShield Administered',
            'Total Doses Administered', 'AEFI', '18-30 years(Age)', '30-45 years(Age)', '45-60 years(Age)',
            '60+ years(Age)'
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
        self.vaccine_state_df.rename(columns={
            'Male(Individuals Vaccinated)': 'Male', 'Female(Individuals Vaccinated)': 'Female',
            'Transgender(Individuals Vaccinated)': 'Transgender', 'AEFI': 'Adverse Event Following Immunization',
            '18-30 years(Age)': 'Age Group 18-30', '30-45 years(Age)': 'Age Group 30-45',
            '45-60 years(Age)': 'Age Group 45-60', '60+ years(Age)': 'Age Group 60+'
        }, inplace=True)
        self.vaccine_state_df.fillna(0.0, axis=1, inplace=True)

        self.vaccine_state_total_df = pd.read_csv(self.path['vaccination']['state_total'])
        self.vaccine_state_total_df.fillna(2832152, axis=1, inplace=True)

        print("All Dataframes Loaded Successfully!")

    def get_current_days_data(self):
        current_stats = dict(self.state_wise_total_df.iloc[0])
        current_vaccine_administered = list(self.vaccine_state_total_df.iloc[-1])[-1]
        current_stats.update({"Vaccine Administered": current_vaccine_administered})
        for not_needed_col in ['State', 'Migrated_Other', 'State_code']:
            current_stats.pop(not_needed_col)
        return current_stats

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

        for col in daily_state_df.columns[2:]:
            daily_state_df[f'Daily {" ".join(col.split())}'] = daily_state_df[col].diff()
        daily_state_df.fillna(0.0, axis=1, inplace=True)

        daily = {
            "state": state,
            "data": [
                {
                    "name": d_type,
                    "x": list(daily_state_df['Date']),
                    "y": list(daily_state_df[d_type])
                }
                for d_type in [
                    'Confirmed', 'Daily Confirmed', 'Recovered', 'Daily Recovered', 'Deceased', 'Daily Deceased',
                    'Tested', 'Daily Tested'
                ]
            ]
        }
        total = {
            "state": state,
            "data": {
                column: col_val for column, col_dict in total_state_df.items() for idx, col_val in col_dict.items()
                if
                column != 'State'
            }
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
        vac_daily_df = self.vaccine_state_df[self.vaccine_state_df["State"] == state]
        # Creating delta columns
        for col in [vc for vc in vac_daily_df.columns if vc not in [
            'Updated On', 'State', 'Adverse Event Following Immunization', 'Age Group 18-30', 'Age Group 30-45',
            'Age Group 45-60', 'Age Group 60+'

        ]]:
            vac_daily_df[f'delta_{"_".join(col.split())}'.lower()] = vac_daily_df[col].diff()
        vac_daily_df.fillna(0.0, axis=1, inplace=True)

        vac_agg_data = vac_daily_df.describe().apply(lambda s: s.apply('{0:.5f}'.format)).to_dict()

        vac_dict = vac_daily_df.to_dict()
        vac_data = {col_name: list(col_val.values()) for col_name, col_val in vac_dict.items()}

        daily = {
            "state": state,
            "data": vac_data
        }
        del vac_data
        return daily, vac_agg_data

    def get_top_states_data(self, top=10):
        state_df = self.state_wise_total_df.copy()
        top_state_total_result = []
        for g_, g_type in enumerate(['Confirmed', 'Active', 'Recovered', 'Deaths']):
            temp = state_df.sort_values(g_type, ascending=False)[['State', g_type]][1:]
            label_l = list(temp['State'][:top])
            data_l = list(temp[g_type][:top])

            top_state_total_result.append({
                "g_title": f"Top 10 {g_type} States",
                "g_id": f"{g_type}_{g_}",
                "g_data": {
                    "labels": label_l,
                    "datasets": [{
                        "label": g_type,
                        "backgroundColor": [COLOR_LIST[i] for i in range(len(label_l))],
                        "data": data_l
                    }]
                }
            })

        return top_state_total_result


if __name__ == "__main__":
    gdf = GraphDataFormatter()
    tot, dly = gdf.get_state_wise_data(state="Maharashtra")
    print("TOTAL DATA--------->")
    print(tot)
    print("="*39)
    print("DAILY DATA--------->")
    print(dly)


