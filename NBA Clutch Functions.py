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




#inputs player level play-by-play data, calculates clutch time dummy, cleans up the time columns to minutes.
#def clean_pbp(pbp_player):      
#    pbp_player['score_diff'] = np.abs(pbp_player['away_score'] - pbp_player['home_score'])
#    pbp_player['clutch_time'] = (pbp_player['remaining_time'] <= '00:05:00') & (pbp_player['period'] == 4) & (pbp_player['score_diff']>= 5) | (pbp_player['period'] == 5)
#    pbp_player['clutch_time'] = np.where(pbp_player['clutch_time'] == True, 1,0)
#    pbp_player['elapsed'] = pd.to_timedelta(pbp_player['elapsed']).astype('timedelta64[s]')
#    pbp_player['remaining_time'] = pd.to_timedelta(pbp_player['remaining_time']).astype('timedelta64[s]')
#    pbp_player['play_length'] = pbp_player['play_length'].str.replace('-12','00')
#    pbp_player['play_length'] = pbp_player['play_length'].str.replace('-5','00')
#    pbp_player['play_length'] = pd.to_timedelta(pbp_player['play_length']).astype('timedelta64[s]')
#    return pbp_player

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



def get_possessions(data):    
    data['steal_PT'] = (pd.notna(data['steal'])).astype(int)
    data['blocks_PT'] = (pd.notna(data['block'])).astype(int)
    data['TO_PT'] = ((pd.notna(data['player']) & (data['event_type'] == 'turnover'))).astype(int)
    data['FGM_PT'] =  ((pd.notna(data['player'])) & (data['event_type'] == 'shot') & (data['result'] == 'made') & ((data['points'] == 2) | (data['points'] == 3)))
    data['3PTM_PT'] = ((pd.notna(data['player'])) & (data['event_type'] == 'shot') & (data['result'] == 'made') & (data['points'] == 3)).astype(int)
    data['FTM_PT'] = ((pd.notna(data['player']))  & (data['event_type'] == 'free throw') & (data['result'] == 'made') & (data['points'] == 1)).astype(int)
    data['Offensive_REB_PT'] = ((pd.notna(data['player'])) & (data['type'] == 'rebound offensive')).astype(int)
    data['Assists_PT'] = (data['player'] == data['assist']).astype(int)
    data['Deffensive_REB_PT'] = ((pd.notna(data['player'])) & (data['type'] == 'rebound deffensive')).astype(int)
    data['Foul_PT'] = ((pd.notna(data['player'])) & (data['event_type'] == 'foul')).astype(int)
    data['FT_Miss_PT'] = ((pd.notna(data['player']))  & (data['event_type'] == 'free throw') & (data['result'] == 'missed') & (data['points'] == 0)).astype(int)
    data['FG_Miss_PT'] = ((pd.notna(data['player']))  & (data['event_type'] == 'miss') & (data['result'] == 'missed')).astype(int)
    #add column for possessions
    data['possessions'] = data['Deffensive_REB_PT'] + data['Offensive_REB_PT'] + data['TO_PT'] + data['FGM_PT'] + data['FTM_PT']/2
    return data 


#input_sched_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Schedules"
#sched_20_21 = r"2020-2021_NBA_Historical_Schedule.csv"
#sched = pd.read_csv(os.path.join(input_sched_path,sched_20_21))

#need to read in schedule first
def add_team(pbp_player, schedule):
    road_sched = schedule[['GAME ID', 'ROAD TEAM']]
    home_sched = schedule[['GAME ID', 'HOME TEAM']]
    road_sched_dict = dict(road_sched.values)
    home_sched_dict = dict(home_sched.values)
    
    home_pivot = pd.melt(pbp_player, id_vars=['data_set','game_id','elapsed', 'play_length',
                                                 "clutch_time", "remaining_time", "player", "steal","block", "assist", "points",
                                                 "event_type", "type", "result", 'possessions'], 
                            value_vars=['h1', 'h2', 'h3', 'h4', 'h5'], 
                            var_name = "position_on_court", value_name = "player_on_court") 
    home_pivot['home_or_away'] = "home"
    home_pivot['home_team'] = home_pivot['game_id'].map(home_sched_dict)
    home_pivot['away_team'] = home_pivot['game_id'].map(road_sched_dict)
    home_pivot['team'] = home_pivot['game_id'].map(home_sched_dict)    
    
    away_pivot = pd.melt(pbp_player, id_vars=['game_id','elapsed', 'play_length',
                                                 "clutch_time", "remaining_time", "player", "steal","block", "assist", "points",
                                                 "event_type", "type", "result", 'possessions'], 
                            value_vars=['a1', 'a2', 'a3', 'a4', 'a5'], 
                            var_name = "position_on_court", value_name = "player_on_court") 
    away_pivot['home_or_away'] = "away"
    away_pivot['home_team'] = away_pivot['game_id'].map(home_sched_dict)
    away_pivot['away_team'] = away_pivot['game_id'].map(road_sched_dict) 
    away_pivot['team'] = away_pivot['game_id'].map(road_sched_dict) 
    
    pbp_pivot = pd.concat([home_pivot, away_pivot], sort=True)
    pbp_pivot['team'] = np.where(pbp_pivot['home_or_away'] == "home", pbp_pivot['home_team'], pbp_pivot['away_team'])

    return pbp_pivot

# takes the 10 player columns and pivots them long, such that there's 10 copies
# of the play. Then calculates PER generated from each type of play. 
def pivot_pbp(pbp_player, year_start, year_end, schedule):
    pbp_pivot = add_team(pbp_player, schedule) 
    pbp_pivot['steal_PER'] = (pbp_pivot['player_on_court'] == pbp_pivot['steal']).astype(int)
    pbp_pivot['blocks_PER'] = (pbp_pivot['player_on_court'] == pbp_pivot['block']).astype(int)
    pbp_pivot['TO_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'turnover')).astype(int)
    pbp_pivot['FGM_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'shot') & (pbp_pivot['result'] == 'made') & ((pbp_pivot['points'] == 2) | (pbp_pivot['points'] == 3))).astype(int)  
    pbp_pivot['3PTM_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['event_type'] == 'shot') & (pbp_pivot['result'] == 'made') & (pbp_pivot['points'] == 3)).astype(int)
    pbp_pivot['FTM_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player'])  & (pbp_pivot['event_type'] == 'free throw') & (pbp_pivot['result'] == 'made') & (pbp_pivot['points'] == 1)).astype(int)
    pbp_pivot['Offensive_REB_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['type'] == 'rebound offensive')).astype(int)
    pbp_pivot['Assists_PER'] = (pbp_pivot['player_on_court'] == pbp_pivot['assist']).astype(int)
    pbp_pivot['Deffensive_REB_PER'] = ((pbp_pivot['player_on_court'] == pbp_pivot['player']) & (pbp_pivot['type'] == 'rebound deffensive')).astype(int)
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
#PER per play is calculated, now aggregate by game
##############################

#group by game, season, player, clutch time or not. 
#creates a df that has 2 rows of boxscore PER for the player, CT and not-CT stats
def game_level_long(pbp_pivot, year_start, year_end):
    pbp_groups = ['game_id','player_on_court', "clutch_time",
                  'home_or_away', 'team']
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
    pbp_grouped['possessions_per_mins_played'] = pbp_grouped['possessions'] / pbp_grouped['play_length_mins']
    return pbp_grouped

# separates df into 2 dfs, CT and Non-CT, then merges on player and game to make data wide
# Once the data is wide, we can regress one column on the other
def game_level_long_to_wide(pbp_grouped, year_start, year_end):
    clutch = pbp_grouped[pbp_grouped["clutch_time"] == 1]
    clutch = clutch.rename(columns={col: col+'_CT' 
                        for col in clutch.columns if col not in ['game_id', 'player_on_court',
                                                                 'home_or_away', 'team', 'home_team', 'away_team']})
    
    not_clutch = pbp_grouped[pbp_grouped["clutch_time"] == 0]
    not_clutch = not_clutch.rename(columns={col: col+'_not_CT' 
                        for col in not_clutch.columns if col not in ['game_id', 'player_on_court',
                                                                     'home_or_away', 'team', 'home_team', 'away_team']})
    
    clutch_merged = pd.merge(not_clutch, clutch, how="outer",on=['data_set',"game_id", "player_on_court",
                                                                 'home_or_away', 'team', 'home_team', 'away_team'])
    clutch_merged["PER_Diff"] = clutch_merged["PER_CT"] - clutch_merged["PER_not_CT"] #this is the PER_diff we want
    clutch_merged['Season'] = str(year_start)+ "-" + str(year_end)
    return clutch_merged
    
   

# Combines all the functions above. Give options to export csv.
def create_clutch_df(input_data_path, year_csv, year_start, year_end, schedule
                     ,export_path, export_game_long = True, export_game_wide = True):
    data_path = os.path.join(input_data_path, year_csv) 
    pbp_player = pd.read_csv(data_path, encoding= 'unicode_escape')
    
    pbp_player = clutch_time_col(pbp_player)
    pbp_player = get_possessions(pbp_player)
    pbp_pivot = pivot_pbp(pbp_player, year_start, year_end, schedule)
    PER_pivot = game_level_long(pbp_pivot, year_start, year_end)
    final_clutch = game_level_long_to_wide(PER_pivot, year_start, year_end)
    
    if export_game_long == True: #exports long data
        long_path = "NBA_clutch_time_PER_long_" +str(year_start) + "_" +str(year_end)+".csv"
        PER_pivot.to_csv(os.path.join(export_path, long_path))
    else:
        pass
    if export_game_wide == True: #exports wide data
        wide_path = "NBA_clutch_time_PER_wide_" +str(year_start) + "_" +str(year_end)+".csv"
        final_clutch.to_csv(os.path.join(export_path, wide_path))    
    else:
        pass
    
    return final_clutch



########################

input_data_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\BDB_data"
export_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs"

def df_list_to_wide(df_list):
    multiple = pd.concat(df_list)
    multiple_short = multiple[['data_set','player_on_court', 'Season', 'PER_CT', 'PER_not_CT', 'PER_Diff']]
    multiple_mean = multiple_short.groupby(['player_on_court', 'data_set','Season']).mean().reset_index()
   
    return multiple_mean


#Adds the year to the end of the columns so the PER columns show the year in the name
#merges on player name.
def make_season_level(df, column = 'Season', remove_nan_inf = True):
    #unique = multiple_mean['Season'].unique().tolist()
    unique = df[column].unique()
    df_list = []
    for i in unique:
        season = df[df[column] == i]
        season = season.rename(columns={col: col+"_"+i 
                        for col in season.columns if col not in ['player_on_court']})
        df_list.append(season)
    combined = pd.merge(df_list[0], df_list[1], how = 'outer', on='player_on_court')
    combined = combined.loc[:, ~combined.columns.str.startswith('Season')]
    #drop instances where players played in one season, but not the other
    if remove_nan_inf == True:
        combined = combined[combined.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]
    return combined

def avg_df_merge_years(df_list, year_start, year_end, column = 'Season', remove_nan_inf = True, export=True):
    wide = df_list_to_wide(df_list)
    final = make_season_level(wide,column = 'Season', remove_nan_inf = True)
    if export == True:
        ungrouped_path = "NBA_PER_Data_" +str(year_start) + "_" +str(year_end)+".csv"
        final.to_csv(os.path.join(export_path, ungrouped_path))       
    return final






