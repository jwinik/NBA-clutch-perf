# -*- coding: utf-8 -*-
"""
Created on Thu May 19 20:38:22 2022

@author: jwini
"""

import pandas as pd
import numpy as np
import os
import statsmodels.api as sm

input_data_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\BDB_data"
one_year = "[12-22-2020]-[07-20-2021]-combined-stats.csv"
raw = pd.read_csv(os.path.join(input_data_path,one_year))


'''
Take play by play data:
- Assign clutch non-clutch time to a play DONE
- Dummy variables for the possession types DONE
- Aggregate plays at the season level DONE
- Count number of possessions DONE
- # of Possessions = Defensive rebound + Offensive Rebound + Turnover + FG made + ( Free Throw Made/2) DONE
- Use that to adjust pace to PER
'''



#data = raw.copy()
#data = clean_pbp(data) #from 'NBA Clutch Functions.py'

#create a list of players. Not needed
def get_player_list(data):
    #make a list of players
    player_cols = ['a1', 'a2', 'a3', 'a4', 'a5', 'h1', 'h2', 'h3', 'h4', 'h5']
    player_list = data[player_cols].values.tolist()
    flat = [item for sublist in player_list for item in sublist]
    flat = list(set(flat))
    return flat
players = get_player_list(data)



#data_dummies = get_possessions(data, players)

#head = data_dummies.head(100)
#input is get_players
def group_season_data(data):
    grouped = data.groupby(['data_set', 'clutch_time']).sum()
    grouped['play_length_mins'] = grouped['play_length'] / 60
    grouped['pace'] = grouped['posessions'] / grouped['play_length_mins']
    return grouped
final = group_season_data(data_dummies)
final = final.reset_index()
trim = final[["data_set", "clutch_time", "posessions", "play_length_mins", "pace"]]

pace_2020_21_CT = trim["pace"][3]
pace_2020_21_not_CT = trim["pace"][2]


