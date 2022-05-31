# -*- coding: utf-8 -*-
"""
Created on Thu May 19 23:06:04 2022

@author: jwini
"""

import statsmodels.api as sm
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

setup_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf"
functions = "NBA Clutch Functions.py"
pace = "NBA Pace Adjustment.py"

setup_files = [functions, pace]
for f in setup_files:
    exec(open(os.path.join(setup_path, f)).read())

#create_clutch_df creates two years of PER data (wide)
sched_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Schedules"
schedule_path_list = ["2006-to-2018_NBA_Historical_Schedule.csv",
                 '2018-2019_NBA_Historical_Schedule.csv',
                 '2020-2021_NBA_Historical_Schedule.csv']

schedule_list = []
for i in schedule_path_list:
    temp = pd.read_csv(os.path.join(sched_path,i))
    schedule_list.append(temp)
    master_schedule = pd.concat(schedule_list)

initials_df = pd.read_csv(r'C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Schedules\Team Initials Mapping.csv')
pace_data = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\team_season_data.csv")

data_10_11_csv = r"[10-20-2010]-[06-30-2011]-combined-stats.csv"
long_10_11, wide_10_11 = create_clutch_df(input_data_path, data_10_11_csv, 2010, 11, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)
data_11_12_csv = r"[10-20-2011]-[07-01-2012]-combined-stats.csv"
long_11_12, wide_11_12 = create_clutch_df(input_data_path, data_11_12_csv, 2011, 12, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)
data_12_13_csv = r"[10-20-2012]-[06-30-2013]-combined-stats.csv"
long_12_13, wide_12_13 = create_clutch_df(input_data_path, data_12_13_csv, 2012, 13, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)
data_13_14_csv = r"[10-20-2013]-[06-30-2014]-combined-stats.csv"
long_13_14, wide_13_14 = create_clutch_df(input_data_path, data_13_14_csv, 2013, 14, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)
data_14_15_csv = r"[10-20-2014]-[06-17-2015]-combined-stats.csv"
long_14_15, wide_14_15 = create_clutch_df(input_data_path, data_14_15_csv, 2014, 15, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)
data_15_16_csv = r"[10-20-2015]-[06-20-2016]-combined-stats.csv"
long_15_16, wide_15_16 = create_clutch_df(input_data_path, data_15_16_csv, 2015, 16, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)


data_16_17_csv = r"[10-25-2016]-[06-12-2017]-combined-stats.csv"
long_16_17, wide_16_17 = create_clutch_df(input_data_path, data_16_17_csv, 2016, 17, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)
data_17_18_csv = r"[10-17-2017]-[06-08-2018]-combined-stats.csv"
long_17_18, wide_17_18 = create_clutch_df(input_data_path, data_17_18_csv, 2017, 18, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)


data_18_19_csv = r"[10-16-2018]-[06-13-2019]-combined-stats.csv"
long_18_19, wide_18_19 = create_clutch_df(input_data_path, data_18_19_csv, 2018, 19, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)


#data_19_20_csv = r"[10-22-2019]-[10-11-2020]-combined-stats.csv"
#long_19_20, wide_19_20 = create_clutch_df(input_data_path, data_19_20_csv, 2019, 20, master_schedule
#                         ,export_path
#                         ,export_game_long = True 
#                         ,export_game_wide = True)

data_20_21_csv = r"[12-22-2020]-[07-20-2021]-combined-stats.csv"
long_20_21, wide_20_21 = create_clutch_df(input_data_path, data_20_21_csv, 2020, 21, master_schedule
                         ,export_path
                         ,export_game_long = True 
                         ,export_game_wide = True)

data_path = os.path.join(input_data_path, data_18_19_csv) 
pbp_player = pd.read_csv(data_path, encoding= 'unicode_escape')
pbp_player = clutch_time_col(pbp_player)
pbp_player = get_possessions(pbp_player)
pbp_pivot = pivot_pbp(pbp_player, 2018, 19, master_schedule)
#PER_pivot = game_level_long(pbp_pivot, 2018, 2019)
#final_clutch = game_level_long_to_wide(PER_pivot, year_start, year_end)
test = pbp_pivot.head(1000)
year_start = 2018
year_end = 19


    







pbp_grouped = get_pace_adjustment(pbp_grouped, pace_data, year_start, year_end)
pbp_grouped['clutch_adj'] = clutch_adj
pbp_grouped.loc[pbp_grouped['clutch_time'] == 0, ['clutch_adj']] = 1 
pbp_grouped['PER_adj'] = pbp_grouped['PER'] * pbp_grouped['Pace Adjustment'] * pbp_grouped['clutch_adj']
return pbp_grouped

#Need to calculate League Average Pace In Clutch time and non clutch time





#Take average stats for the season, then regress one year on the other.

# Going to turn the below into a function. But stacks 2 years of game level data
# then takes the average PER (PER_CT, PER_not_CT, PER_diff) for both years (6 columns)

df_list_19_21 = [season_20_21, season_19_20]
df_list_18_20 = [season_18_19, season_19_20]

clean_19_21 = avg_df_merge_years(df_list_19_21, '2019', '2021')
clean_18_20 = avg_df_merge_years(df_list_18_20) 

#Does PER_diff from year 1 impact year 2?
simple_YOY_ols(clean_19_21, "PER_Diff_2020-2021", "PER_Diff_2019-2020")
simple_YOY_ols(clean_18_20, "PER_Diff_2019-2020", "PER_Diff_2018-2019")


























output_data_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs"
season_20_21_fname = "NBA_clutch_time_PER_ungrouped_2020_2021.csv"

season_20_21 = pd.read_csv(os.path.join(output_data_path, season_20_21_fname))

#pace comes from another script
season_20_21['PER_pace'] = np.where(season_20_21['clutch_time']!= 1, season_20_21['PER'] / pace_2020_21_CT, season_20_21['PER'] / pace_2020_21_not_CT)

season = season_20_21[['player_on_court',"clutch_time", "PER_pace"]]
#season = pd.get_dummies(season, columns=['player_on_court'], drop_first=True)
season.replace([np.inf, -np.inf], np.nan, inplace=True)
season.to_csv(r'C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\season_dummies_2020_21.csv', index = False)

result = smf.ols('PER_pace ~ C(player_on_court) + C(clutch_time) + C(player_on_court) * C(clutch_time)', data = season).fit()
print(result.summary())

print(result.wald_test)
results = pd.DataFrame()
def results_summary_to_dataframe(results):
    '''This takes the result of an statsmodel results table and transforms it into a dataframe'''
    pvals = results.pvalues
    coeff = results.params
    conf_lower = results.conf_int()[0]
    conf_higher = results.conf_int()[1]

    results_df = pd.DataFrame({"pvals":pvals,
                               "coeff":coeff,
                               "conf_lower":conf_lower,
                               "conf_higher":conf_higher
                                })

    #Reordering...
    results_df = results_df[["coeff","pvals","conf_lower","conf_higher"]]
    return results_df


result_df = results_summary_to_dataframe(result)
result_df = result_df.reset_index()
result_df.to_csv(r'C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\season_regression_2020_21.csv', index = False)


# Residual vs fitted plot
plt.figure(figsize=(8,6))
sns.residplot(result.fittedvalues, result.resid, lowess=True)
plt.xlabel("Fitted values", fontsize=15)
plt.ylabel("Residuals", fontsize=15)
plt.title('Residual vs fitted plot', fontsize=20)    

