# -*- coding: utf-8 -*-
"""
Created on Sun May  8 13:08:11 2022

@author: jwini
"""

import pandas as pd
import numpy as np
import os
import statsmodels.api as sm



'''
Play by Play Data
'''


def clean_pbp(pbp_player):      
    pbp_player['score_diff'] = np.abs(pbp_player['away_score'] - pbp_player['home_score'])
    pbp_player['clutch_time'] = (pbp_player['remaining_time'] <= '00:05:00') & (pbp_player['period'] == 4) & (pbp_player['score_diff']>= 5) | (pbp_player['period'] == 5)
    pbp_player['clutch_time'] = np.where(pbp_player['clutch_time'] == True, 1,0)
    pbp_player['elapsed'] = pd.to_timedelta(pbp_player['elapsed']).astype('timedelta64[s]')
    pbp_player['remaining_time'] = pd.to_timedelta(pbp_player['remaining_time']).astype('timedelta64[s]')
    pbp_player['play_length'] = pbp_player['play_length'].str.replace('-12','00')
    pbp_player['play_length'] = pbp_player['play_length'].str.replace('-5','00')
    pbp_player['play_length'] = pd.to_timedelta(pbp_player['play_length']).astype('timedelta64[s]')
    return pbp_player


def pivot_pbp(pbp_player, year_start, year_end):
    pbp_pivot = pd.melt(pbp_player, id_vars=['game_id', 'elapsed', 'play_length',
                                             "clutch_time", "remaining_time", "player", "steal","block", "assist", "points",
                                             "event_type", "result"], 
                        value_vars=['a1', 'a2', 'a3', 'a4', 'a5', 'h1', 'h2',
           'h3', 'h4', 'h5'], var_name = "position_on_court", value_name = "player_on_court") 
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
    #pbp_pivot['Season'] = str(year_start)+ "-" + str(year_end)
    return pbp_pivot



###############################
#Data is calculated, now aggregate by game
##############################
def game_level_clutch_df(pbp_pivot, year_start, year_end):
    pbp_groups = ['game_id','player_on_court', "clutch_time"]
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
    return pbp_grouped

def make_game_level_again(pbp_grouped, year_start, year_end):
    clutch = pbp_grouped[pbp_grouped["clutch_time"] == 1]
    clutch = clutch.rename(columns={col: col+'_CT' 
                        for col in clutch.columns if col not in ['game_id', 'player_on_court']})
    
    not_clutch = pbp_grouped[pbp_grouped["clutch_time"] == 0]
    not_clutch = not_clutch.rename(columns={col: col+'_not_CT' 
                        for col in not_clutch.columns if col not in ['game_id', 'player_on_court']})
    
    clutch_merged = pd.merge(not_clutch, clutch, how="outer",on=["game_id", "player_on_court"])
    clutch_merged["PER_Diff"] = clutch_merged["PER_CT"] - clutch_merged["PER_not_CT"]
    clutch_merged['Season'] = str(year_start)+ "-" + str(year_end)
    return clutch_merged
    
   

# Combining them
def create_clutch_df(input_data_path, year_csv, year_start, year_end
                     ,export_path, export_game_ungrouped = True, export_game_grouped = True):
    data_path = os.path.join(input_data_path, year_csv) 
    pbp_player = pd.read_csv(data_path)
    
    pbp_player = clean_pbp(pbp_player)
    pbp_pivot = pivot_pbp(pbp_player, year_start, year_end)
    PER_pivot = game_level_clutch_df(pbp_pivot, year_start, year_end)
    final_clutch = make_game_level_again(PER_pivot, year_start, year_end)
    
    if export_game_ungrouped == True:
        ungrouped_path = "NBA_clutch_time_PER_ungrouped_" +str(year_start) + "_" +str(year_end)+".csv"
        PER_pivot.to_csv(os.path.join(export_path, ungrouped_path))
    else:
        pass
    if export_game_grouped == True:
        grouped_path = "NBA_clutch_time_PER_grouped_" +str(year_start) + "_" +str(year_end)+".csv"
        final_clutch.to_csv(os.path.join(export_path, grouped_path))    
    else:
        pass
    
    return final_clutch



########### Just do it #############
input_data_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\BDB_data"
export_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs"

data_19_20_csv = r"[10-22-2019]-[10-11-2020]-combined-stats.csv"
season_19_20 = create_clutch_df(input_data_path, data_19_20_csv, 2019, 2020
                         ,export_path
                         ,export_game_ungrouped = True 
                         ,export_game_grouped = True)

data_20_21_csv = r"[12-22-2020]-[07-20-2021]-combined-stats.csv"
season_20_21 = create_clutch_df(input_data_path, data_20_21_csv, 2020, 2021
                         ,export_path
                         ,export_game_ungrouped = True 
                         ,export_game_grouped = True)

#Take average stats for the season, then regress one year on the other.

multiple = pd.concat([season_20_21, season_19_20])

multiple_short = multiple[['player_on_court', 'Season', 'PER_CT', 'PER_not_CT', 'PER_Diff']]

multiple_mean = multiple_short.groupby(['player_on_court', 'Season']).mean().reset_index()
multiple_agg = multiple_short.groupby(['player_on_court', 'Season']).agg(
    'Avg_PER_CT' )


unique = multiple_mean['Season'].unique().tolist()


def make_season_level(df, column = 'Season'):
    unique = df[column].unique()
    df_list = []
    for i in unique:
        season = df[df[column] == i]
        #season = season.drop('Season')
        season = season.rename(columns={col: col+"_"+i 
                        for col in season.columns if col not in ['player_on_court']})
        df_list.append(season)
        #print(season.columns)
    combined = pd.merge(df_list[0], df_list[1], how = 'outer', on='player_on_court')
    combined = combined.loc[:, ~combined.columns.str.startswith('Season')]
    return combined

test = make_season_level(multiple_mean, 'Season')
clean = test[test.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]


X = clean['PER_Diff_2019-2020']
Y = clean['PER_Diff_2020-2021']
X = sm.add_constant(X)
model = sm.OLS(Y, X).fit()
summary = model.summary()
print(summary)
