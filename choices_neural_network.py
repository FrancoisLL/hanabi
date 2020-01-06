# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 10:48:49 2019

@author: flelay
"""

from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error 
from matplotlib import pyplot as plt
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings 
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=DeprecationWarning)
from xgboost import XGBRegressor

from random import randrange

from game_functions import discard, play_card, give_info, check_end_game
from classes import game

###############################################################################
########## neural network model building ######################################
###############################################################################

def nn_model(data):
    
    data = data.sample(frac=1).reset_index(drop=True)
    target = data['score']
    
    NN_model = Sequential()
    
    # The Input Layer :
    NN_model.add(Dense(128, kernel_initializer='normal',input_dim = data.shape[1], activation='relu'))
    
    # The Hidden Layers :
    NN_model.add(Dense(256, kernel_initializer='normal',activation='relu'))
    NN_model.add(Dense(256, kernel_initializer='normal',activation='relu'))
    NN_model.add(Dense(256, kernel_initializer='normal',activation='relu'))
    
    # The Output Layer :
    NN_model.add(Dense(1, kernel_initializer='normal',activation='linear'))
    
    # Compile the network :
    NN_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])

    checkpoint_name = 'Weights-{epoch:03d}--{val_loss:.5f}.hdf5' 
    checkpoint = ModelCheckpoint(checkpoint_name, monitor='val_loss', verbose = 1, save_best_only = True, mode ='auto')
    callbacks_list = [checkpoint]

    NN_model.fit(data, target, epochs=500, batch_size=32, validation_split = 0.2, callbacks=callbacks_list)

#    # Load wights file of the best model :
#    wights_file = 'Weights-478--18738.19831.hdf5' # choose the best checkpoint 
#    NN_model.load_weights(wights_file) # load it
#    NN_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])

    return NN_model

###############################################################################
########## random forest model ################################################
###############################################################################

def rf_model(data):
    
    labels = np.array(data['score'])
    features = data.drop('score', 1)
    
#    feature_list = list(features.columns)

    features = np.array(features)
    
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25)
    

    rf_model = RandomForestRegressor(n_estimators = 1000)

    rf_model.fit(train_features, train_labels);
    
#    predictions = rf.predict(test_features)
#    
#    errors = abs(predictions - test_labels)
#
#    print('Mean Absolute Error:', round(np.mean(errors), 4))
#
#
#    mape = 100 * (errors / test_labels)
#    accuracy = 100 - np.mean(mape)
#    print('Accuracy:', round(accuracy, 2), '%.')    
#    
#    importances = list(rf_model.feature_importances_)
#    feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]
#    feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)
#    [print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances];
    
    return rf_model
    
    
###############################################################################
########## game main function #################################################
###############################################################################
    
def launch_game_nn(players_number, display, model):
    
    # use a constant seed for the tests
    #seed(123)
    g = game()
    g.deal_cards(players_number)
    
    first_player = randrange(players_number)
    current_player = first_player
    
    ## create the game state dataframe
    colors_list = ['blue', 'red', 'green', 'yellow', 'white']
    values_list = [1, 2, 3, 4, 5]
    cards_in_deck_indexes = [0, 1, 2, 3]
    next_players_indexes = range(1, players_number)
    # general game information
    game_state = pd.DataFrame(columns = ['info_tokens', 'error_tokens', 'blue_firework', 
                'red_firework', 'green_firework', 'yellow_firework', 'white_firework'])
    # discard pile composition
    for color in colors_list:
        for value in values_list:
            game_state[str(value) + " " + color + " in the discard pile"] = None
    # player deck
    for card in cards_in_deck_indexes:
        for color in colors_list:
            game_state["info : card " + str(card) + " is " + color] = None
        for value in values_list:
            game_state["info : card " + str(card) + " is " + str(value)] = None
    # next players' decks
    for player in next_players_indexes:
        for card in cards_in_deck_indexes:
            for color in colors_list:
                game_state["player " + str(player) + " turn(s) after : card " + str(card) + " is " + color] = None
            for value in values_list:
                game_state["player " + str(player) + " turn(s) after : card " + str(card) + " is " + str(value)] = None
    # next players' deck information
    for player in next_players_indexes:
        for card in cards_in_deck_indexes:
            for color in colors_list:
                game_state["player " + str(player) + " turn(s) after : info : card " + str(card) + " is " + color] = None
            for value in values_list:
                game_state["player " + str(player) + " turn(s) after : info : card " + str(card) + " is " + str(value)] = None       
    # choices
    for card in cards_in_deck_indexes:
        game_state["play card " + str(card)] = None
        game_state["discard card " + str(card)] = None
    for player in next_players_indexes:
        for color in colors_list:
            game_state["say to player " + str(player) + " the " + color] = None
        for value in values_list:
            game_state["say to player " + str(player) + " the " + str(value)] = None
    game_state.loc[0] = 0
            
    end_game = False
    no_draw_pile_counter = 0
    if display:
        turn_number = 0
        print(g)
        print("turn number :", turn_number)
        print("first player :", first_player)
        print("__________________________________________________________")
    
    # the game starts from here
    while not(end_game):
        neural_network_predictions(g, g.players[current_player], players_number, game_state, model)
        if display:
            turn_number += 1
            if turn_number < 100:
                print(g)
                print("")
                print("turn_number :", turn_number)
                print("current player :", current_player)
                print("__________________________________________________________")
        end_game, no_draw_pile_counter = check_end_game(g, no_draw_pile_counter)
        
        current_player = (current_player + 1) % players_number
       
    # Results display
    if g.error_tokens == 0:
        lost = True
        if display:
            print("game lost")
    else:
        lost = False
    
    return g, sum(g.fireworks.values()), lost

###############################################################################
########## neural network predictions for each turn ###########################
###############################################################################
    
def neural_network_predictions(g, p, players_number, game_state, model):
    colors_list = ['blue', 'red', 'green', 'yellow', 'white']
    values_list = [1, 2, 3, 4, 5]
    
    ## encode the game state
    game_state.loc[0, 'info_tokens'] = g.info_tokens
    game_state.loc[0, 'error_tokens'] = g.error_tokens
    for color in ['blue', 'red', 'green', 'yellow', 'white']:
        game_state.loc[0, color + '_firework'] = g.fireworks[color]
    
    # deck information
    for c in p.deck:
        if c.color_info != "":
            game_state.loc[0, 'info : card ' + str(p.deck.index(c)) + ' is ' + str(c.color_info)] = 1
        if c.value_info != 10:
            game_state.loc[0, 'info : card ' + str(p.deck.index(c)) + ' is ' + str(c.value_info)] = 1
                
    # next players' deck
    for next_turn in range(1, players_number):
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        card_index = 0
        for c in next_player_deck:
            game_state.loc[0, 'player ' + str(next_turn) + ' turn(s) after : card ' + str(card_index) + ' is ' + str(c.color)] = 1
            game_state.loc[0, 'player ' + str(next_turn) + ' turn(s) after : card ' + str(card_index) + ' is ' + str(c.value)] = 1
            card_index += 1
    
    # next players' deck information
    for next_player in range(1, players_number):
        next_player_deck = g.players[((g.players.index(p)) + next_player) % players_number].deck
        for c in next_player_deck:
            if c.color_info != "":
                game_state.loc[0, 'player ' + str(next_player) + ' turn(s) after : info : card ' + str(next_player_deck.index(c)) + ' is ' + str(c.color_info)] = 1
            if c.value_info != 10:
                game_state.loc[0, 'player ' + str(next_player) + ' turn(s) after : info : card ' + str(next_player_deck.index(c)) + ' is ' + str(c.value_info)] = 1
    
    ## make a score prediction for each possible action and choose the best one  

    if len(p.deck) == 4:
        possible_actions = list(game_state.columns[[392, 394, 396, 398]])
    else:
        possible_actions = list(game_state.columns[[392, 394, 396]])

    if g.info_tokens != 8:
        if len(p.deck) == 4:
            possible_actions += list(game_state.columns[[393, 395, 397, 399]])
        else:
            possible_actions += list(game_state.columns[[393, 395, 397]])
        
    if g.info_tokens > 0:
        for next_player in range(1, players_number):
            next_player_deck = g.players[((g.players.index(p)) + next_player) % players_number].deck
            
            for color in colors_list:
                for c in next_player_deck:
                    if c.color == color:
                        possible_actions.append('say to player ' + str(next_player) + ' the ' + color)
                        break
                
            for value in values_list:             
                for c in next_player_deck:
                    if c.value == value:
                        possible_actions.append('say to player ' + str(next_player) + ' the ' + str(value))
                        break               

    action_to_do = ""
    highest_action_score = -100
    for action in possible_actions:
        game_state.loc[0, 392:440] = 0
        game_state.loc[0, action] = 1
        action_score = model.predict(game_state).item()
        if action_score > highest_action_score:
            action_to_do = action
            highest_action_score = action_score
            
    ## execute the chosen action
    if 'play card' in action_to_do:
        play_card(g, p, p.deck[int(action_to_do[10])])
        return
    
    if 'discard card' in action_to_do:
        discard(g, p, p.deck[int(action_to_do[13])])
        return
    
    if 'say' in action_to_do:
        if ('blue' in action_to_do) or ('red' in action_to_do) or ('green' in action_to_do) or ('yellow' in action_to_do) or ('white' in action_to_do):
            give_info(g, g.players[(g.players.index(p) + int(action_to_do[14])) % players_number], 'color', action_to_do[20:len(action_to_do)])
            return
        else:
            give_info(g, g.players[(g.players.index(p) + int(action_to_do[14])) % players_number], 'value', int(action_to_do[20]))
            return

    
    
    




































