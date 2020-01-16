# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 14:16:57 2019

@author: flelay
"""

import numpy as np
import matplotlib.pyplot as plt
from statistics import median
from time import time

from classes import game
from choices_by_rules import launch_game, saved_launch_game
from create_data_for_neural_network import data_creation
from choices_neural_network import nn_model, rf_model, launch_game_nn
from genetic_algorithm_rules import launch_game_genetic, genetic_algorithm

players_number = 5

########## launch one game with displays ######################################

#g, score, lost = launch_game(players_number, display = True)

########## launch several games to measure accuracy ###########################

games_number = 10000
res = []
res_error_tokens = []
games_lost = []
for i in range(games_number):
    g, score, lost, error_tokens = launch_game(players_number, display = False)
    res.append(score)
    res_error_tokens.append(error_tokens)
    games_lost.append(lost)

print("max score :", max(res))
print("min score :", min(res))
print("mean score :", np.mean(res))
print("median score :", median(res))
print("standard deviation :", np.std(res))
print("games lost :", 100 * sum(games_lost) / games_number, "%")
plt.hist(res)
#print("error tokens at the end of the game :")
#plt.hist(res_error_tokens)


########## launch games until a given score ###################################

#score = 10
#games_counter = 0
#while score > 4:
#    games_counter += 1
#    data_game, first_player, score, lost = saved_launch_game(players_number, display = False)
#
#print(data_game[0])
#turn_number = 0
#current_player = first_player
#print("turn number :", turn_number)
#print("first player :", current_player)
#print("__________________________________________________________")
#for g in data_game:
#    turn_number += 1
#    print(g)
#    print("")
#    print("turn number :", turn_number)
#    print("current_player :", current_player)
#    print("__________________________________________________________")
#    current_player = (current_player + 1) % players_number


########## create a large dataset for the neural network ######################

#t1 = time()
#games_number = 10
#
#data = data_creation(players_number, games_number)
#t2 = time()
#
#print("games number :", games_number)
#print("execution time :", '%.3f'%(t2 - t1), "seconds")

#data.to_csv(r'C:\Users\flelay\Documents\tests\hanabi\data.csv', index = None, header = True)
#
########## build the model and launch a game ###################

##model = nn_model(data)
#
#model = rf_model(data)
#
##g, score, lost = launch_game_rnn(players_number, True, model)
#
#games_number = 10
#res = []
#games_lost = []
#for i in range(games_number):
#    g, score, lost = launch_game_nn(players_number, False, model)
#    res.append(score)
#    games_lost.append(lost)
#
#print("max score :", max(res))
#print("min score :", min(res))
#print("mean score :", np.mean(res))
#print("median score :", median(res))
#print("standard deviation :", np.std(res))
#print("games lost :", 100 * sum(games_lost) / games_number, "%")
#plt.hist(res)

########## launch several genetic games to measure accuracy ###################

#games_number = 1000
#res = []
#games_lost = []
#for i in range(games_number):
#    g = game()    
#    g.deal_cards(players_number)
#    g, score, lost = launch_game_genetic(g, False)
#    res.append(score)
#    games_lost.append(lost)
#
#print("max score :", max(res))
#print("min score :", min(res))
#print("mean score :", np.mean(res))
#print("median score :", median(res))
#print("standard deviation :", np.std(res))
#print("games lost :", 100 * sum(games_lost) / games_number, "%")
#plt.hist(res)

########## genetic algorithm ##################################################

#games_number = 100
#repetitions = 10
#children_number = int(games_number / 2)
#generations_number = 100
#
#scores, last_generation_genomes = genetic_algorithm(players_number, games_number, repetitions, children_number, generations_number)















