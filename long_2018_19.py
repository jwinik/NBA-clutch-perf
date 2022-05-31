# -*- coding: utf-8 -*-
"""
Created on Sat May 28 23:56:58 2022

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

setup_files = [functions]
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


######################################

data_18_19_csv = r"[10-16-2018]-[06-13-2019]-combined-stats.csv"
year_start = 2018
year_end = 19

data_path = os.path.join(input_data_path, data_18_19_csv) 
pbp_player = pd.read_csv(data_path, encoding= 'unicode_escape')
pbp_player = clutch_time_col(pbp_player)
pbp_player = get_possessions(pbp_player)
pbp_pivot = pivot_pbp(pbp_player, year_start, year_end, master_schedule)
#PER_pivot = game_level_long(pbp_pivot, year_start, 2019)
#final_clutch = game_level_long_to_wide(PER_pivot, year_start, year_end)

#game_level_long
pbp_groups = ['game_id','player_on_court', "clutch_time",
              'home_or_away', 'team', 'home_team', 'away_team', 'opponent']
pivot_head = pbp_pivot.head(1000)
pbp_grouped = pbp_pivot.groupby(pbp_groups).sum()
pbp_grouped['play_length_mins'] = pbp_grouped['play_length'] / 60 
pbp_grouped['PER'] = (pbp_grouped['FGM_PER'] * 85.91
                    + pbp_grouped['steal_PER'] * 53.897
                    + pbp_grouped['3PTM_PER'] * 51.757
                    + pbp_grouped['FTM_PER'] *46.845
                    + pbp_grouped['blocks_PER'] * 39.190
                    + pbp_grouped['Offensive_REB_PER'] * 39.190
                    + pbp_grouped['Assists_PER'] * 34.677
                    + pbp_grouped['Deffensive_REB_PER'] * 14.707
                    - pbp_grouped['FT_Miss_PER'] * 20.091
                    - pbp_grouped['FG_Miss_PER'] * 39.190
                    - pbp_grouped['TO_PER'] * 53.897) * (1/pbp_grouped['play_length_mins'])
pbp_grouped = pbp_grouped.reset_index()
#pbp_grouped['above_500_mins'] = np.where(pbp_grouped['play_length_mins'] >= 500,1,0)
pbp_grouped['Season'] = str(year_start)+ "-" + str(year_end)
pbp_grouped['possessions_per_mins_played'] = pbp_grouped['possessions'] / pbp_grouped['play_length_mins']
clutch_adj = get_clutch_adjustment(pbp_grouped)


clutch_df = pbp_grouped[['clutch_time', 'possessions', 'play_length']]
clutch_df = clutch_df.groupby(['clutch_time']).agg(
    possessions = ('possessions', 'sum'),
    time_played = ('play_length', 'sum'))
clutch_df = clutch_df.reset_index()
clutch_df['league_pace'] = clutch_df['possessions'] / clutch_df['time_played']
clutch_pace = clutch_df['league_pace'][0]
not_clutch_pace = clutch_df['league_pace'][1]
clutch_adj = not_clutch_pace / clutch_pace













