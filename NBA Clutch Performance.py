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
box_player = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20\Boxscore - Player\NBA-2019-2020-Player-BoxScore-Dataset.csv")


def good_players_list(box_player_df, min_minutes, filter = True):
    box_sum = box_player_df.groupby('PLAYER \nFULL NAME').agg(
    MIN = pd.NamedAgg(column='MIN', aggfunc=sum),
    FG = pd.NamedAgg(column='FG', aggfunc=sum),
    FGA = pd.NamedAgg(column='FGA', aggfunc=sum),
    Three_P = pd.NamedAgg(column='3P', aggfunc=sum),
    Three_PA = pd.NamedAgg(column='3PA', aggfunc=sum),
    FT = pd.NamedAgg(column='FT', aggfunc=sum),
    FTA = pd.NamedAgg(column='FTA', aggfunc=sum),
    OR = pd.NamedAgg(column='OR', aggfunc=sum),
    DR = pd.NamedAgg(column='DR', aggfunc=sum),
    TOT = pd.NamedAgg(column='TOT', aggfunc=sum),
    A = pd.NamedAgg(column='A', aggfunc=sum),
    PF = pd.NamedAgg(column='PF', aggfunc=sum),
    ST = pd.NamedAgg(column='ST', aggfunc=sum),
    TO = pd.NamedAgg(column='TO', aggfunc=sum),
    BL = pd.NamedAgg(column='BL', aggfunc=sum),
    PTS = pd.NamedAgg(column='PTS', aggfunc=sum))
    title = "above_" + str(min_minutes)+"mins"
    
    box_sum[title] = np.where(box_sum['MIN'] >= min_minutes, 1, 0)
    box_sum['Season'] = box_player_df['BIGDATABALL\nDATASET'][0]
    year = box_sum.pop('Season')
    box_sum.insert(0, "Season", year)
    
    if filter == True:
        box_sum = box_sum[box_sum['MIN'] >= min_minutes]
    else:
        box_sum = box_sum
    return box_sum

season_stats_above_500_min = good_players_list(box_player, 500, filter=False)

export_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20"
min_500_path = "season_stats_above_500_min.csv"

season_stats_above_500_min.to_csv(os.path.join(export_path, min_500_path))


# Was a play clutch?

#pbp_player = pbp_player[(pbp_player['remaining_time'] <= '00:05:00')]
pbp_player['score_diff'] = np.abs(pbp_player['away_score'] - pbp_player['home_score'])
pbp_player['clutch_time'] = (pbp_player['remaining_time'] <= '00:05:00') & (pbp_player['period'] == 4) & (pbp_player['score_diff']>= 5)

def clutch_var(df):
    df['clutch_time'] = np.where(df[''])