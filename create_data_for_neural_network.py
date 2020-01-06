# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:31:33 2019

@author: flelay
"""

import numpy as np
import pandas as pd
from random import randrange

from classes import game
from game_functions import turn_player_data_neural_network, check_end_game

###############################################################################
########## set columns names of the dataframe #################################
###############################################################################

def create_data_columns(players_number):
    colors_list = ['blue', 'red', 'green', 'yellow', 'white']
    values_list = [1, 2, 3, 4, 5]
    cards_in_deck_indexes = [0, 1, 2, 3]
    next_players_indexes = range(1, players_number)
    
    ## set the input columns names
    
    # general game information
    data = pd.DataFrame(columns = ['info_tokens', 'error_tokens', 'blue_firework', 
                'red_firework', 'green_firework', 'yellow_firework', 'white_firework'])
    
    # discard pile composition
    for color in colors_list:
        for value in values_list:
            data[str(value) + " " + color + " in the discard pile"] = None
    
    # player deck
    for card in cards_in_deck_indexes:
        for color in colors_list:
            data["info : card " + str(card) + " is " + color] = None
        for value in values_list:
            data["info : card " + str(card) + " is " + str(value)] = None
    
    # next players' decks
    for player in next_players_indexes:
        for card in cards_in_deck_indexes:
            for color in colors_list:
                data["player " + str(player) + " turn(s) after : card " + str(card) + " is " + color] = None
            for value in values_list:
                data["player " + str(player) + " turn(s) after : card " + str(card) + " is " + str(value)] = None
    
    # next players' deck information
    for player in next_players_indexes:
        for card in cards_in_deck_indexes:
            for color in colors_list:
                data["player " + str(player) + " turn(s) after : info : card " + str(card) + " is " + color] = None
            for value in values_list:
                data["player " + str(player) + " turn(s) after : info : card " + str(card) + " is " + str(value)] = None       
    
    # choices
    for card in cards_in_deck_indexes:
        data["play card " + str(card)] = None
        data["discard card " + str(card)] = None
    
    for player in next_players_indexes:
        for color in colors_list:
            data["say to player " + str(player) + " the " + color] = None
        for value in values_list:
            data["say to player " + str(player) + " the " + str(value)] = None
    
    ## set the output columns names
    
    data['score_evolution_turn+1'] = None
    data['error'] = None
    data['info_tokens_evolution'] = None
    data['score_evolution_turn+5'] = None
    data['final_score'] = None
    data['errors_turn+5'] = None
    data['game_lost'] = None

    return data
    
###############################################################################
########## launch several games to add data rows ##############################
###############################################################################

# main function that calls the function for just one game few times
def data_creation(players_number, games_number):
    
    data = create_data_columns(players_number)
    contents = pd.DataFrame(np.zeros(shape = (games_number * 70, data.shape[1])), columns = data.columns)
    data = pd.concat([data, contents])    

    index = 0    
    for n in range(games_number):
        data, index = add_data_with_one_game(data, players_number, index)
    
    data = data.loc[~(data==0).all(axis=1)]
    
    # compute the score of each turn
    data['score'] = data['score_evolution_turn+1'] * 10 - data['error'] * 20 + data['info_tokens_evolution'] * 2 + data['score_evolution_turn+5'] * 4  + data['final_score'] * 0.1 - data['errors_turn+5'] * 8 - data['game_lost'] * 3
    data.drop(['score_evolution_turn+1', 'error', 'info_tokens_evolution', 'score_evolution_turn+5', 'final_score', 'errors_turn+5', 'game_lost'], 1, inplace = True)    
    
    # normalize the columns beetween 0 and 1
    data = (data - data.min()) / (data.max() - data.min())
    data.fillna(0, inplace = True)
    
    return data


# function that fill the dataframe with one game
def add_data_with_one_game(data, players_number, index):
    
    g = game()
    g.deal_cards(players_number)
    
    first_player = randrange(players_number)
    current_player = first_player
    
    end_game = False
    no_draw_pile_counter = 0
    
    starting_index = index
    
    turn_type = 'first'
    
#    # display
#    turn_number = 0
#    print(g)
#    print("")
#    print("turn_number :", turn_number)
#    print("first player :", first_player)
#    print("__________________________________________________________")
    
    while not(end_game):
        data = turn_player_data_neural_network(g, players_number, g.players[current_player], data, turn_type, index)
        turn_type = 'regular'
        index += 1
        
#        turn_number += 1
#        if turn_number < 17:
#            print(g)
#            print("")
#            print("turn_number :", turn_number)
#            print("current player :", current_player)
#            print("next player :", (current_player + 1) % players_number)
#            print("__________________________________________________________")
    
        end_game, no_draw_pile_counter = check_end_game(g, no_draw_pile_counter)
        
        current_player = (current_player + 1) % players_number
      
    # update the game results
    data.loc[starting_index:index - 1, 'final_score'] = sum(g.fireworks.values())
    data.loc[starting_index:index - 1, 'game_lost'] = int(g.error_tokens == 0)
    
    # update the "turn+5" features
    for i in range(index - players_number):
        data.loc[i, 'score_evolution_turn+5'] = sum(data.loc[i:i + 4, 'score_evolution_turn+1'])
        data.loc[i, 'errors_turn+5'] = sum(data.loc[i:i + 4, 'error'])
    for i in range(index - players_number, index):
        data.loc[i, 'score_evolution_turn+5'] = sum(data.loc[i:index - 1, 'score_evolution_turn+1'])
        data.loc[i, 'errors_turn+5'] = sum(data.loc[i:index - 1, 'error'])

    # clear the last row, that is altered by this game but is actually for the next game
    data.loc[index] = 0

    return data, index
















































