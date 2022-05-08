# -*- coding: utf-8 -*-
"""
Created on Mon May  2 13:44:14 2022

@author: jwini
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime


''''
Box Score
'''
box_player = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20\Boxscore - Player\NBA-2019-2020-Player-BoxScore-Dataset.csv")

cols = box_player.columns.tolist()


for element in sample_list:
    converted_list.append(element.strip())


def calc_PER(df):
    df['PER'] = (df['FG'] * 85.91
    + df['ST'] * 53.897
    + df['Three_P'] * 51.757
    + df['FT'] *46.845
    + df['BL'] * 39.190
    + df['OR'] * 39.190
    + df['A'] * 34.677
    + df['DR'] * 14.707
    - (df['FTA'] - df['FT']) + 20.091
    - (df['FGA'] - df['FG']) + 39.190
    - df['TO'] * 53.897) * (1/df['MIN'])
    return df
    


groups = ['PLAYER \nFULL NAME', 'GAME-ID','DATE','PLAYER-ID','POSITION','OWN \nTEAM','OPPONENT \nTEAM',
'VENUE\n(R/H)','STARTER\n(Y/N)']

def good_players_list(box_player_df, min_minutes, filter = False):
    box_sum = box_player_df.groupby(groups).agg(
    MIN = pd.NamedAgg(column='MIN', aggfunc=sum),
    FG = pd.NamedAgg(column='FG', aggfunc=sum), #FG Made
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
    
    box_sum['PER'] = calc_PER(box_sum)
    
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

season_stats_above_500_min = season_stats_above_500_min.reset_index()



'''
All together
'''
main_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Box_Score\Data"
years_list = ["NBA-2016-2017-Player-BoxScore-Dataset.xlsx", 
              "NBA-2017-2018-Player-BoxScore-Dataset.xlsx",
              "NBA-2018-2019-Player-BoxScore-Dataset.xlsx",
              "NBA-2019-2020-Player-BoxScore-Dataset.xlsx",
              "NBA-2020-2021-Player-BoxScore-Dataset.xlsx"]

box_16_17 = pd.read_excel(os.path.join(main_path, years_list[0]), engine="openpyxl")
box_17_18 = pd.read_excel(os.path.join(main_path, years_list[1]), engine="openpyxl")
box_18_19 = pd.read_excel(os.path.join(main_path, years_list[2]), engine="openpyxl")
box_19_20 = pd.read_excel(os.path.join(main_path, years_list[3]), engine="openpyxl")
box_20_21 = pd.read_excel(os.path.join(main_path, years_list[4]), engine="openpyxl")
#box_player = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\Data_19_20\Boxscore - Player\NBA-2019-2020-Player-BoxScore-Dataset.csv")

box_20_21 = pd.read_excel()


def get_PER_box(df, playoffs = False, season_string, min_minutes):
    
    