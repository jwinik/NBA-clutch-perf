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

data_16_17_csv = r"[10-25-2016]-[06-12-2017]-combined-stats.csv"
season_16_17 = create_clutch_df(input_data_path, data_16_17_csv, 2016, 2017
                         ,export_path
                         ,export_game_ungrouped = True 
                         ,export_game_grouped = True)
data_17_18_csv = r"[10-17-2017]-[06-08-2018]-combined-stats.csv"
season_17_18 = create_clutch_df(input_data_path, data_17_18_csv, 2017, 2018
                         ,export_path
                         ,export_game_ungrouped = True 
                         ,export_game_grouped = True)


data_18_19_csv = r"[10-16-2018]-[06-13-2019]-combined-stats.csv"
season_18_19 = create_clutch_df(input_data_path, data_18_19_csv, 2018, 2019
                         ,export_path
                         ,export_game_ungrouped = True 
                         ,export_game_grouped = True)


data_19_20_csv = r"[10-22-2019]-[10-11-2020]-combined-stats.csv"
season_19_20 = create_clutch_df(input_data_path, data_19_20_csv, 2019, 2020
                         ,export_path
                         ,export_game_ungrouped = True 
                         ,export_game_grouped = True)

data_20_21_csv = r"[12-22-2020]-[07-20-2021]-combined-stats.csv"
season_20_21 = create_clutch_df(input_data_path, data_20_21_csv, 2020, 2021
                         ,export_path
                         ,export_game_ungrouped = False 
                         ,export_game_grouped = False)

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

