# -*- coding: utf-8 -*-
"""
Created on Mon May 30 21:55:56 2022

@author: jwini
"""
import pandas as pd
import os
import path
import seaborn as sns
import numpy as np



import_path = r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs"
data_15_16 = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\NBA_clutch_time_PER_wide_2015_16.csv")
data_16_17 = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\NBA_clutch_time_PER_wide_2016_17.csv")
data_17_18 = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\NBA_clutch_time_PER_wide_2017_18.csv")
data_18_19 = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\NBA_clutch_time_PER_wide_2018_19.csv")
data_20_21 = pd.read_csv(r"C:\Users\jwini\Documents\Gtihub Repositories\NBA-clutch-perf\in_game_analysis\Outputs\NBA_clutch_time_PER_wide_2020_21.csv")

set_1 = [data_15_16,data_16_17]
set_2 = [data_16_17, data_17_18]
set_3 = [data_17_18, data_18_19]
set_4 = [data_18_19, data_20_21]