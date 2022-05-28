# -*- coding: utf-8 -*-
"""
Created on Mon May 23 11:23:43 2022

@author: jwini
"""

import pandas as pd
import os
import numpy as np

input_data_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\BDB_data"
data_path = r"[12-22-2020]-[07-20-2021]-combined-stats.csv"

data = pd.read_csv(os.path.join(input_data_path, data_path))
first_game_id = 22000019
filtered = data[data['game_id'] == first_game_id]

filtered = filtered.reset_index()
filtered = filtered.rename(columns = {'index':"play_number"})
filtered['score_diff'] = np.abs(filtered['away_score'] - filtered['home_score'])

filtered['clutch_time'] = ((filtered['remaining_time'] <= '00:05:00') & (filtered['period'] == 4) & (filtered['score_diff']>= 5) | (filtered['period'] == 5)).astype(int)
filtered['elapsed'] = pd.to_timedelta(filtered['elapsed']).astype('timedelta64[s]')
filtered['remaining_time'] = pd.to_timedelta(filtered['remaining_time']).astype('timedelta64[s]')
filtered['play_length'] = filtered['play_length'].str.replace('-12','00')
filtered['play_length'] = filtered['play_length'].str.replace('-5','00')
filtered['play_length'] = pd.to_timedelta(filtered['play_length']).astype('timedelta64[s]')


clutch_plays = filtered[filtered['clutch_time'] == 1]
first_clutch_play_index = min(clutch_plays['play_number'])

filtered['clutch_time'] = np.where(filtered['play_number'] >= first_clutch_play_index,1,0)




##################### Function #########

def clutch_time_col(data):
    game_list = []
    game_id_list = data.game_id.unique().tolist()
    for id in game_id_list:
        filtered = data[data['game_id'] == id]
        
        filtered = filtered.reset_index()
        filtered = filtered.rename(columns = {'index':"play_number"})
        filtered['score_diff'] = np.abs(filtered['away_score'] - filtered['home_score'])
        filtered['clutch_time'] = ((filtered['remaining_time'] <= '00:05:00') & (filtered['period'] == 4) & (filtered['score_diff']>= 5) | (filtered['period'] == 5)).astype(int)
        filtered['elapsed'] = pd.to_timedelta(filtered['elapsed']).astype('timedelta64[s]')
        filtered['remaining_time'] = pd.to_timedelta(filtered['remaining_time']).astype('timedelta64[s]')
        filtered['play_length'] = filtered['play_length'].str.replace('-12','00')
        filtered['play_length'] = filtered['play_length'].str.replace('-5','00')
        filtered['play_length'] = pd.to_timedelta(filtered['play_length']).astype('timedelta64[s]')
        
        
        clutch_plays = filtered[filtered['clutch_time'] == 1]
        if clutch_plays.empty:
            game_list.append(filtered)
        else:
            first_clutch_play_index = min(clutch_plays['play_number'])
            
            filtered['clutch_time'] = np.where(filtered['play_number'] >= first_clutch_play_index,1,0)
            
            game_list.append(filtered)
    data_clean = pd.concat(game_list)
    return data_clean


test = clutch_time_col(data)
        
clutch_plays = test[test['clutch_time'] == 1]

check = test[test['game_id'] == 	22000855]
