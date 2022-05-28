# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 19:48:46 2022

@author: jwini
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

pbp_player = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20\Play by Play - Player\[10-22-2019]-[10-11-2020]-combined-stats.csv")

export_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20"

'''
Play by Play Data
'''

# Was a play clutch?

#pbp_player = pbp_player[(pbp_player['remaining_time'] <= '00:05:00')]
pbp_player['score_diff'] = np.abs(pbp_player['away_score'] - pbp_player['home_score'])
pbp_player['clutch_time'] = (pbp_player['remaining_time'] <= '00:05:00') & (pbp_player['period'] == 4) & (pbp_player['score_diff']>= 5) | (pbp_player['period'] == 5)
pbp_player['clutch_time'] = np.where(pbp_player['clutch_time'] == True, 1,0)


#pbp_player['elapsed'] = pd.to_datetime(pbp_player['elapsed'],format= '%H:%M:%S' ).dt.time

#pbp_player['elapsed'] = pd.to_datetime(pbp_player['elapsed'])
#pbp_player['elapsed'] = [time.time() for time in pbp_player['elapsed']]

pbp_player['elapsed'] = pd.to_timedelta(pbp_player['elapsed']).astype('timedelta64[s]')
pbp_player['remaining_time'] = pd.to_timedelta(pbp_player['remaining_time']).astype('timedelta64[s]')
pbp_player['play_length'] = pbp_player['play_length'].str.replace('-12','00')
pbp_player['play_length'] = pbp_player['play_length'].str.replace('-5','00')
pbp_player['play_length'] = pd.to_timedelta(pbp_player['play_length']).astype('timedelta64[s]')

time_variables = ["remaining_time", "elapsed"]

#def strings_to_time(df, variables):
#    for v in variables:
#        if df[v].dtype == "object":
#            df[v] = pd.to_timedelta(df[v])
#    return df

#test = strings_to_time(pbp_player, time_variables)

#pivot players on the court
pbp_pivot = pd.melt(pbp_player, id_vars=['game_id', 'elapsed', 'play_length',
                                         "clutch_time", "remaining_time", "player", "steal","block", "assist", "points",
                                         "event_type", "result"], 
                    value_vars=['a1', 'a2', 'a3', 'a4', 'a5', 'h1', 'h2',
       'h3', 'h4', 'h5'], var_name = "position_on_court", value_name = "player_on_court")

################# Calculate PER ##############

pbp_pivot['steal_PER'] = (pbp_pivot['player_on_court'] == pbp_pivot['steal']).astype(int)
pbp_pivot['blocks_PER'] = (pbp_pivot['player_on_court'] == pbp_pivot['block']).astype(int)
pbp_pivot['TO_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'turnover')).astype(int)
pbp_pivot['FGM_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'shot') & (pbp_pivot['result'] == 'made') & ((pbp_pivot['points'] == 2) | (pbp_pivot['points'] == 3))).astype(int)  
pbp_pivot['3PTM_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'shot') & (pbp_pivot['result'] == 'made') & (pbp_pivot['points'] == 3)).astype(int)
pbp_pivot['FTM_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player'])  & (pbp_pivot['event_type'] == 'free throw') & (pbp_pivot['result'] == 'made') & (pbp_pivot['points'] == 1)).astype(int)
pbp_pivot['Offensive_REB_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'rebound offensive')).astype(int)
pbp_pivot['Assists_PER'] = (pbp_pivot['player_on_court'] == pbp_pivot['assist']).astype(int)
pbp_pivot['Deffensive_REB_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'rebound deffensive')).astype(int)
pbp_pivot['Foul_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'foul')).astype(int)
pbp_pivot['FT_Miss_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player'])  & (pbp_pivot['event_type'] == 'free throw') & (pbp_pivot['result'] == 'missed') & (pbp_pivot['points'] == 0)).astype(int)
pbp_pivot['FG_Miss_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player'])  & (pbp_pivot['event_type'] == 'miss') & (pbp_pivot['result'] == 'missed')).astype(int)

pbp_pivot['PER_no_min'] = (pbp_pivot['FGM_PER'] * 85.91
                    + pbp_pivot['steal_PER'] * 53.897
                    + pbp_pivot['3PTM_PER'] * 51.757
                    + pbp_pivot['FTM_PER'] *46.845
                    + pbp_pivot['blocks_PER'] * 39.190
                    + pbp_pivot['Offensive_REB_PER'] * 39.190
                    + pbp_pivot['Assists_PER'] * 34.677
                    + pbp_pivot['Deffensive_REB_PER'] * 14.707
                    - pbp_pivot['FT_Miss_PER'] * 20.091
                    - pbp_pivot['FG_Miss_PER'] * 39.190
                    - pbp_pivot['TO_PER'] * 53.897)

test = pbp_pivot.head(1000)

#pbp_pivot_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20"
pbp_path = "pbp_with_clutch_time.csv"
pbp_pivot.to_csv(os.path.join(export_path, pbp_path))








###############################
#Data is calculated, now aggregate by game
##############################
pbp_groups = ['game_id','player_on_court', "clutch_time"]

pbp_cols = ['elapsed', 'play_length', 'remaining_time', 'player',
     'steal', 'block', 'assist', 'points', 'event_type', 'result', 'position_on_court',
     'steal_PER', 'blocks_PER', 'TO_PER', 'FGM_PER', '3PTM_PER', 
     'FTM_PER', 'Offensive_REB_PER', 'Deffensive_REB_PER', 'Assists_PER', 'Foul_PER', 
     'FT_Miss_PER', 'FG_Miss_PER', 'PER_no_min']



#pbp_grouped = pbp_pivot.groupby(pbp_groups).agg(
#    elapsed_sum = pd.NamedAgg(column='elapsed', aggfunc=sum),
#    play_length_sum = pd.NamedAgg(column='play_length', aggfunc=sum),
#    remaining_time_sum = pd.NamedAgg(column='remaining_time', aggfunc=sum),
#    FGM_PER = pd.NamedAgg(column='FGM_PER', aggfunc=sum),
#    steal_PER = pd.NamedAgg(column='remaining_time', aggfunc=sum),
#    ThreePTM_PER = pd.NamedAgg(column='3PTM_PER', aggfunc=sum),
#    FTM_PER = pd.NamedAgg(column='FTM_PER', aggfunc=sum),
#    blocks_PER = pd.NamedAgg(column='blocks_PER', aggfunc=sum),
#   Offensive_REB_PER = pd.NamedAgg(column='Offensive_REB_PER', aggfunc=sum),
#   Assists_PER = pd.NamedAgg(column='Assists_PER', aggfunc=sum),
#   Deffensive_REB_PER = pd.NamedAgg(column='Deffensive_REB_PER', aggfunc=sum),
#   FT_Miss_PER = pd.NamedAgg(column='FT_Miss_PER', aggfunc=sum),
#    FG_Miss_PER = pd.NamedAgg(column='FG_Miss_PER', aggfunc=sum),
#    TO_PER = pd.NamedAgg(column='TO_PER', aggfunc=sum),
#    PER_no_min = pd.NamedAgg(column='PER_no_min', aggfunc=sum))

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
pbp_grouped['above_500_mins'] = np.where(pbp_grouped['play_length_mins'] >= 500,1,0)


clutch_path = "NBA_clutch_time_PER_2019_2020.csv"
pbp_grouped.to_csv(os.path.join(export_path, clutch_path))





