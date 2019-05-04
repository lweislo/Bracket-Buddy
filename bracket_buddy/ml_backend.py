import os
import random

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.backend import clear_session
from keras.models import load_model
from KDEpy import FFTKDE

from bracket_buddy.ml_data_stats import mean as ml_stats_mean, std as ml_stats_std
from bracket_buddy.year_team_std import year_team_std
from bracket_buddy.name_map import home_court
import bracket_buddy.ml_data_stats

clear_session()
model_path = os.path.join('bracket_buddy', 'data', 'ml_data', 'first_model.h5')
model = load_model(model_path)
graph = tf.get_default_graph()

cols = ['AdjTempo', 'AdjOE', 'AdjDE', 'eFG_Pct_O', 'eFG_Pct_D',
        'TO_Pct_O', 'TO_Pct_D', 'OR_Pct_O', 'OR_Pct_D', 'FT_Rate_O',
        'FT_Rate_D', 'OFF_FT', 'OFF_2PT', 'OFF_3PT', 'DEF_FT',
        'DEF_2PT', 'DEF_3PT', 'Size', 'Hgt1', 'Hgt2', 'Hgt3', 'Hgt4',
        'Hgt5', 'HgtEff', 'Exp', 'Bench', 'Pts1', 'Pts2', 'Pts3', 'Pts4',
        'Pts5', 'OR1', 'OR2', 'OR3', 'OR4', 'OR5', 'DR1', 'DR2', 'DR3',
        'DR4', 'DR5', 'FG2Pct', 'FG3Pct', 'FTPct', 'BlockPct',
        'OppFG2Pct', 'OppFG3Pct', 'OppFTPct', 'OppBlockPct', 'F3GRate',
        'OppF3GRate', 'ARate', 'OppARate', 'StlRate', 'OppStlRate']


def get_random_number():
    rand = random.random()
    rand = ((rand * 2) - 1) / 20
    return rand


def prepare_data(year1, team1, year2, team2, mongo):
    data = []
    team_year_info = mongo.db.basketball.find_one(
        {'TeamName': str(team1), 'Season': int(year1)})
    for col in cols:
        data.append(team_year_info[col])
    team_year_info = mongo.db.basketball.find_one(
        {'TeamName': str(team2), 'Season': int(year2)})
    for col in cols:
        data.append(team_year_info[col])
    data.append(home_court.get(str(team1), 0))
    data = np.array(data)
    return data


def randomize_data(year1, team1, year2, team2, data):
    data_std = year_team_std[year1].get(team1, year_team_std['all'])
    cols_len = len(cols)
    data_copy = data.copy()
    data_copy[0] += get_random_number() * data_std['Pace']
    data_copy[1] += get_random_number() * data_std['ORtg']
    data_copy[2] += get_random_number() * data_std['DRtg']
    data_copy[3] += get_random_number() * data_std['OeFG%']
    data_copy[4] += get_random_number() * data_std['DeFG%']
    data_copy[5] += get_random_number() * data_std['OTOV%']
    data_copy[6] += get_random_number() * data_std['DTOV%']
    data_copy[7] += get_random_number() * data_std['OORB%']
    data_copy[8] += get_random_number() * data_std['DDRB%']
    data_copy[9] += get_random_number() * data_std['OFT/FGA']
    data_copy[10] += get_random_number() * data_std['DFT/FGA']
    data_copy[41] += get_random_number() * data_std['hFG%']
    data_copy[42] += get_random_number() * data_std['h3P%']
    data_copy[43] += get_random_number() * data_std['hFT%']
    data_copy[44] += get_random_number() * data_std['BLK%']
    data_copy[49] += get_random_number() * data_std['h3PA']
    data_copy[51] += get_random_number() * data_std['AST%']
    data_copy[53] += get_random_number() * data_std['STL%']
    data_std = year_team_std[year2].get(team2, year_team_std['all'])
    data_copy[0 + cols_len] += get_random_number() * data_std['Pace']
    data_copy[1 + cols_len] += get_random_number() * data_std['ORtg']
    data_copy[2 + cols_len] += get_random_number() * data_std['DRtg']
    data_copy[3 + cols_len] += get_random_number() * data_std['OeFG%']
    data_copy[4 + cols_len] += get_random_number() * data_std['DeFG%']
    data_copy[5 + cols_len] += get_random_number() * data_std['OTOV%']
    data_copy[6 + cols_len] += get_random_number() * data_std['DTOV%']
    data_copy[7 + cols_len] += get_random_number() * data_std['OORB%']
    data_copy[8 + cols_len] += get_random_number() * data_std['DDRB%']
    data_copy[9 + cols_len] += get_random_number() * data_std['OFT/FGA']
    data_copy[10 + cols_len] += get_random_number() * data_std['DFT/FGA']
    data_copy[41 + cols_len] += get_random_number() * data_std['hFG%']
    data_copy[42 + cols_len] += get_random_number() * data_std['h3P%']
    data_copy[43 + cols_len] += get_random_number() * data_std['hFT%']
    data_copy[44 + cols_len] += get_random_number() * data_std['BLK%']
    data_copy[49 + cols_len] += get_random_number() * data_std['h3PA']
    data_copy[51 + cols_len] += get_random_number() * data_std['AST%']
    data_copy[53 + cols_len] += get_random_number() * data_std['STL%']

    return data_copy


def monte_carlo(year1, team1, year2, team2, mongo):
    output = {}
    data = prepare_data(year1, team1, year2, team2, mongo)
    data_df = pd.DataFrame(data.reshape(1, 111))
    data_copy = data.copy()
    num_trials = 99
    for i in range(num_trials):
        rand_data = randomize_data(year1, team1, year2, team2, data_copy)
        data_df.loc[len(data_df)] = rand_data
    data_df -= ml_stats_mean
    data_df = data_df / ml_stats_std
    global graph
    with graph.as_default():
        prediction = model.predict(data_df)
    estimator = FFTKDE(kernel='gaussian', bw='silverman')
    over_under = [x for x in prediction[:, 0] + prediction[:, 1]]
    spread = [x for x in prediction[:, 0] - prediction[:, 1]]
    home_wins = 0
    for i in range(num_trials + 1):
        if prediction[i, 0] > prediction[i, 1]:
            home_wins += 1
    home_win_pct = home_wins / (num_trials + 1)
    est_win_pct = round((home_win_pct * 200) - 100)
    output['est_win_pct'] = str(est_win_pct)
    oe_x, oe_y = estimator.fit(over_under, weights=None).evaluate()
    s_x, s_y = estimator.fit(spread, weights=None).evaluate()
    output['home_points'] = [str(x) for x in prediction[:, 0]]
    output['away_points'] = [str(x) for x in prediction[:, 1]]
    output['over_under_x'] = [str(x) for x in oe_x]
    output['over_under_y'] = [str(x) for x in oe_y]
    output['spread_x'] = [str(x) for x in s_x]
    output['spread_y'] = [str(x) for x in s_y]
    output['over_under'] = str(round(np.mean(over_under), 1))
    output['spread'] = str(round(np.mean(spread), 1))
    return output