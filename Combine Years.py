# -*- coding: utf-8 -*-
"""
Created on Mon May 30 11:03:56 2022

@author: jwini
"""

import pandas as pd
import os
import path
import seaborn as sns
import numpy as np



import_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs"
data_15_16 = "NBA_clutch_time_PER_wide_2015_16.csv"
data_16_17 = "NBA_clutch_time_PER_wide_2016_17.csv"
data_17_18 = "NBA_clutch_time_PER_wide_2017_18.csv"
data_18_19 = "NBA_clutch_time_PER_wide_2018_19.csv"
data_19_20 = "NBA_clutch_time_PER_wide_2020_21.csv"

import_list = [data_15_16, data_16_17, data_17_18, data_18_19, data_19_20]

data_list = []
for i in import_list:
    temp = pd.read_csv(os.path.join(import_path, i))
    data_list.append(temp)

wide = pd.concat(data_list)
wide_head = wide.head(1000)

#remove columns where a player only plays reg time, or only clutch time
#df2=df.dropna(subset=['Courses','Fee'])
wide_clean = wide.dropna(subset=['clutch_time_not_CT', "clutch_time_CT"])
wide_clean.to_csv(os.path.join(import_path, "PER_wide_game_CT_and_not_CT.csv"))


season_wide_clean = wide_clean.groupby(["player_on_court", "team", "Season"]).sum().reset_index()
season_wide_clean['harmonic_sum_mins'] = (season_wide_clean["play_length_mins_CT"] * season_wide_clean["play_length_mins_not_CT"]) / (season_wide_clean["play_length_mins_CT"] + season_wide_clean["play_length_mins_not_CT"])
season_wide_clean['Season'] = season_wide_clean['Season'].astype("category") 


#season_wide_clean.replace([np.inf, -np.inf], 0, inplace=True)



season_wide_clean.to_csv(os.path.join(import_path, "PER_wide_season_CT_and_not_CT.csv"))

#clutch games played for a player
mapping_gp = season_wide_clean[["player_on_court","clutch_time_CT"]]
mapping_gp = mapping_gp.groupby("player_on_court").sum().reset_index()
mapping_gp_dict = dict(mapping_gp.values)

hsm = season_wide_clean[["player_on_court","harmonic_sum_mins"]]
hsm = hsm.groupby("player_on_court").sum().reset_index()
hsm_dict = dict(hsm.values)


#filter only players who played in clutch time
clutch_players = list(set(season_wide_clean['player_on_court']))
#filter only games played in clutch time
clutch_game_id = list(set(season_wide_clean['game_id']))



#Now create a merged long dataset, map it

long_data_15_16 = "NBA_clutch_time_PER_long_2015_16.csv"
long_data_15_16 = "NBA_clutch_time_PER_long_2016_17.csv"
long_data_17_18 = "NBA_clutch_time_PER_long_2017_18.csv"
long_data_18_19 = "NBA_clutch_time_PER_long_2018_19.csv"
long_data_19_20 = "NBA_clutch_time_PER_long_2020_21.csv"

import_list = [long_data_15_16, long_data_15_16, long_data_17_18, long_data_18_19, long_data_19_20]




data_list_long = []
for i in import_list:
    temp = pd.read_csv(os.path.join(import_path, i))
    data_list_long.append(temp)
long = pd.concat(data_list_long)

#long.to_csv(os.path.join(import_path, "long_data_all_seasons.csv"))

long = long[long['player_on_court'].isin(clutch_players)]
long = long[long['game_id'].isin(clutch_game_id)]
long['games_played'] = long['player_on_court'].map(mapping_gp_dict)

long['harmonic_sum_mins'] = long['player_on_court'].map(hsm_dict)

long_na = long[pd.isnull(long['PER_adj'])]












long.to_csv(os.path.join(import_path, "long_data_all_seasons.csv"))


############ Figures ####################
sns.histplot(data=season_wide_clean, x="harmonic_sum_mins", bins=15)

sns.barplot(data=season_wide_clean, x="Season", y="harmonic_sum")
