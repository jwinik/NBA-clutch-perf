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


# takes the 10 player columns and pivots them long, such that there's 10 copies
# of the play. Then calculates PER generated from each type of play. 
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
#PER per play is calculated, now aggregate by game
##############################

#group by game, season, player, clutch time or not. 
#creates a df that has 2 rows of boxscore PER for the player, CT and not-CT stats
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

# separates df into 2 dfs, CT and Non-CT, then merges on player and game to make data wide
# Once the data is wide, we can regress one column on the other
def make_game_level_again(pbp_grouped, year_start, year_end):
    clutch = pbp_grouped[pbp_grouped["clutch_time"] == 1]
    clutch = clutch.rename(columns={col: col+'_CT' 
                        for col in clutch.columns if col not in ['game_id', 'player_on_court']})
    
    not_clutch = pbp_grouped[pbp_grouped["clutch_time"] == 0]
    not_clutch = not_clutch.rename(columns={col: col+'_not_CT' 
                        for col in not_clutch.columns if col not in ['game_id', 'player_on_court']})
    
    clutch_merged = pd.merge(not_clutch, clutch, how="outer",on=["game_id", "player_on_court"])
    clutch_merged["PER_Diff"] = clutch_merged["PER_CT"] - clutch_merged["PER_not_CT"] #this is the PER_diff we want
    clutch_merged['Season'] = str(year_start)+ "-" + str(year_end)
    return clutch_merged
    
   

# Combines all the functions above. Give options to export csv.
def create_clutch_df(input_data_path, year_csv, year_start, year_end
                     ,export_path, export_game_ungrouped = True, export_game_grouped = True):
    data_path = os.path.join(input_data_path, year_csv) 
    pbp_player = pd.read_csv(data_path, encoding= 'unicode_escape')
    
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

def df_list_to_wide(df_list):
    multiple = pd.concat(df_list)
    multiple_short = multiple[['player_on_court', 'Season', 'PER_CT', 'PER_not_CT', 'PER_Diff']]
    multiple_mean = multiple_short.groupby(['player_on_court', 'Season']).mean().reset_index()
#multiple_agg = multiple_short.groupby(['player_on_court', 'Season']).agg(
#    'Avg_PER_CT' )
    
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

def avg_df_merge_years(df_list, column = 'Season', remove_nan_inf = True):
    wide = df_list_to_wide(df_list)
    final = make_season_level(wide,column = 'Season', remove_nan_inf = True)
    return final

clean_19_21 = avg_df_merge_years(df_list_19_21)
clean_18_20 = avg_df_merge_years(df_list_18_20) 





#Does PER_diff from year 1 impact year 2?
def simple_ols(df, dep, ind):
    X = df[str(ind)]
    Y = df[str(dep)]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    summary = model.summary()
    print(summary)
    
simple_ols(clean_19_21, "PER_Diff_2020-2021", "PER_Diff_2019-2020")
simple_ols(clean_18_20, "PER_Diff_2019-2020", "PER_Diff_2018-2019")
