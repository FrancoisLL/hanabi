# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 14:17:20 2019

@author: flelay
"""

import numpy as np

from useful_functions import info_to_give, info_given_to_player, unseen_information, several_playable_cards, color_lost

###############################################################################
########## action functions ###################################################
###############################################################################

def discard(g, p, c):
    g.discard_pile.append(c)
    
    p.deck.remove(c)
    
    # draw a card if possible
    if len(g.draw_pile) > 0:
        p.deck.append(g.draw_pile[0])
        del g.draw_pile[0]
    
    g.info_tokens += 1
    
    
def play_card(g, p, c):
    p.deck.remove(c)
    
    # build the firework if possible
    if c.value == g.fireworks[c.color] + 1:
        g.fireworks[c.color] += 1
        # earn an info token when a firework is completed
        if g.fireworks[c.color] == 5:
            g.info_tokens += 1
    
    # loose an error token if the card does not fit in and discard it
    else:
        g.error_tokens -= 1
        g.discard_pile.append(c)
        
    # draw a card if possible
    if len(g.draw_pile) > 0:
        p.deck.append(g.draw_pile[0])
        del g.draw_pile[0]
    
    
def give_info(g, player_info, info_type, info):
    g.info_tokens -= 1
    
    if info_type == 'color':
        for c in player_info.deck:
            if c.color == info:
                c.color_info = info
        
    else:
        for c in player_info.deck:
            if c.value == info:
                c.value_info = info
    
    
def check_end_game(g, no_draw_pile_counter):
    end_game = False
    
    if len(g.draw_pile) == 0:
        no_draw_pile_counter += 1
    
    if (sum(g.fireworks.values()) == 25) or (no_draw_pile_counter == len(g.players) + 1) or (g.error_tokens == 0):
        end_game = True   
    
    return end_game, no_draw_pile_counter



###############################################################################
########## special function that updates the dataframe for neural network #####
###############################################################################            
        
def turn_player_data_neural_network(g, players_number, p, data, turn_type, index):
    
    if turn_type == 'first':
        data = data_game_initialization(data, g, g.players.index(p), index)
    else:
        ## update the game information
            
        # cards
        for next_player in range(players_number - 2):
            data.iloc[index, 72 + 40 * next_player:111 + 40 * next_player] = np.array(data.iloc[index - 1, 72 + 40 * (next_player + 1):111 + 40 * (next_player + 1)])
        last_next_player_deck = g.players[(g.players.index(p) + players_number - 1) % players_number].deck
        card_index = 0
        for c in last_next_player_deck:
            data.loc[index, 'player ' + str(players_number - 1) + ' turn(s) after : card ' + str(card_index) + ' is ' + str(c.color)] = 1
            data.loc[index, 'player ' + str(players_number - 1) + ' turn(s) after : card ' + str(card_index) + ' is ' + str(c.value)] = 1
            card_index += 1 
        
        # cards info
        for c in p.deck:
            if c.color_info != "":
                data.loc[index, 'info : card ' + str(p.deck.index(c)) + ' is ' + str(c.color_info)] = 1
            if c.value_info != 10:
                data.loc[index, 'info : card ' + str(p.deck.index(c)) + ' is ' + str(c.value_info)] = 1
                
        for next_player in range(1, players_number):
            next_player_deck = g.players[((g.players.index(p)) + next_player) % players_number].deck
            for c in next_player_deck:
                if c.color_info != "":
                    data.loc[index, 'player ' + str(next_player) + ' turn(s) after : info : card ' + str(next_player_deck.index(c)) + ' is ' + str(c.color_info)] = 1
                if c.value_info != 10:
                    data.loc[index, 'player ' + str(next_player) + ' turn(s) after : info : card ' + str(next_player_deck.index(c)) + ' is ' + str(c.value_info)] = 1
        
    # play a card if the information on it is known and can be played
    # discard it if the card is useless
    for c in p.deck:
        if (c.color_info != "") and (c.value_info != 10):
            if c.value_info <= g.fireworks[c.color_info]:
                data = discard_neural_network(g, p, players_number, c, data, index)
                return data
            else:
                data = play_card_neural_network(g, p, players_number, c, data, index)
                return data
        elif c.color_info != "":
            if (g.fireworks[c.color_info] == 5) or (color_lost(g, c.color)):
                data = discard_neural_network(g, p, players_number, c, data, index)
                return data
            else:
                data = play_card_neural_network(g, p, players_number, c, data, index)
                return data
        elif c.value_info != 10:
            if (c.value_info < 5) and (c.value_info <= min(g.fireworks.values())):
                data = discard_neural_network(g, p, players_number, c, data, index)
                return data
            elif c.value_info < 5:
                data = play_card_neural_network(g, p, players_number, c, data, index)
                return data
    
    # give the information if a player among the 2 nexts has 2 playable cards
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            recurrent_value = several_playable_cards(g, next_player_deck)
            if recurrent_value != 0:
                good_info = True
                for c in next_player_deck:
                    if (c.value == recurrent_value) and (c.color_info == "") and (c.value_info == 10):
                        if (not(unseen_information(g, next_player, c, 'value'))) or (not(unseen_information(g, next_player, c, 'color'))) or (c.value < g.fireworks[c.color] + 1):
                            good_info = False
                if good_info:
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', recurrent_value, data, index)
                    return data
    
    # give an information if the 2 next players have nice cards with not any info on it
    # and if there is at least an info token left
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck: 
                if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                    info = info_to_give(next_player_deck, c)
                    if info == "color":
                        if unseen_information(g, next_player, c, 'color'):
                            data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                            return data
                    elif info == "value":
                        if unseen_information(g, next_player, c, 'value'):
                            data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', c.value, data, index)
                            return data
                    
    # give an information to a player if the previous player has an information so the second one
    # will be able to play a card just after (second and third next players)
    if g.info_tokens >= 1:
        for next_turn in [2, 3]:
            player_before_next = g.players[(g.players.index(p) + next_turn - 1) % players_number]
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value == g.fireworks[c.color] + 2) and (c.color_info == "") and (c.value_info == 10) and info_given_to_player(player_before_next, c.color, g.fireworks[c.color] + 1):
                    info = info_to_give(next_player_deck, c)
                    if info == "color":
                        if unseen_information(g, next_player, c, 'color'):
                            data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                            return data
                    elif info == "value":
                        if unseen_information(g, next_player, c, 'value'):
                            data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', c.value, data, index)
                            return data
                    
    # give an information about a "5" or a useless card in the 2 next players' deck
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', 5, data, index)
                    return data
                elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', c.value, data, index)
                    return data
                elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                    return data
                
    # give an information if the next players have nice cards with not any info on it
    # and if there is at least an info token left (from the third next player)
    if g.info_tokens >= 1:
        for next_turn in range(3, players_number):
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                    info = info_to_give(next_player_deck, c)
                    if info == "color":
                        if unseen_information(g, next_player, c, 'color'):
                            data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                            return data
                    elif info == "value":
                        if unseen_information(g, next_player, c, 'value'):
                            data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', c.value, data, index)
                            return data  
    
    # give an information about a "5" or a useless card in the next players' deck (from the third next player)
    if g.info_tokens >= 1:
        for next_turn in range(3, players_number):
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', 5, data, index)
                    return data
                elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'value', c.value, data, index)
                    return data
                elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                    return data
    
    # complete the information about a "5" of the next players
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == "") and (g.fireworks[c.color] == 4):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                    return data
    
    # try to put a random card if the game is almost done and there are still error tokens
    if (len(g.draw_pile) < 4) and g.error_tokens >= 2:
        for c in p.deck:
            if (c.color_info == "") and (c.value_info == 10):
                data = play_card_neural_network(g, p, players_number, c, data, index)
                return data
    
    # throw a card (not a useful 5) if no information about the deck
    if g.info_tokens < 8:
        for c in p.deck:
            if c.value_info != 5:
                data = discard_neural_network(g, p, players_number, c, data, index)
                return data
    
    # complete the information about a "5" to not discard randomly
    # favor the "5" with no cards with the same color in the deck
    if g.info_tokens >= 1:
        for next_turn in range(1, players_number):
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    if info_to_give(next_player_deck, c) == 'color':
                        data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                        return data
                    
        for next_turn in range(1, players_number):
            next_player = g.players[(g.players.index(p) + next_turn) % players_number]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    data = give_info_neural_network(g, g.players.index(p), players_number, next_player, 'color', c.color, data, index)
                    return data             
                    
    # play a random card (rarely happens)
    for c in p.deck:
        if (c.color_info == "") and (c.value_info == 10):
            data = play_card_neural_network(g, p, players_number, c, data, index)
            return data
    for c in p.deck:
        if (c.color_info == "") and (c.value_info != 5):
            data = play_card_neural_network(g, p, players_number, c, data, index)
            return data
    for c in p.deck:
        if (c.color_info == "") or (c.value_info != 10):
            data = play_card_neural_network(g, p, players_number, c, data, index)
            return data


###############################################################################
########## action functions for neural network ################################
###############################################################################

def discard_neural_network(g, p, players_number, c, data, index):
    index_card = p.deck.index(c)
    
    g.discard_pile.append(c)
    
    p.deck.remove(c)
    
    # draw a card if possible
    if len(g.draw_pile) > 0:
        p.deck.append(g.draw_pile[0])
        del g.draw_pile[0]
    
    g.info_tokens += 1
    
    data.loc[index, 'discard card ' + str(index_card)] = 1
    data.loc[index, 'info_tokens_evolution'] = 1
    data.loc[index + 1, 'info_tokens'] = data.loc[index, 'info_tokens'] + 1
    
    # game information and discard pile
    data.iloc[index + 1, 1:31] = np.array(data.iloc[index, 1:31])
    data.loc[index + 1, str(c.value) + ' ' + str(c.color) + ' in the discard pile'] += 1
       
    return data
    

def play_card_neural_network(g, p, players_number, c, data, index):
    index_card = p.deck.index(c)
    
    p.deck.remove(c)
    
    data.loc[index, 'play card ' + str(index_card)] = 1
    
    # game information and discard pile
    data.iloc[index + 1, 0:31] = np.array(data.iloc[index, 0:31])
    
    # build the firework if possible
    if c.value == g.fireworks[c.color] + 1:
        g.fireworks[c.color] += 1
        data.loc[index, 'score_evolution_turn+1'] = 1
        data.loc[index + 1, str(c.color) + '_firework'] = data.loc[index, str(c.color) + '_firework'] + 1
        
        # earn an info token when a firework is completed
        if g.fireworks[c.color] == 5:
            g.info_tokens += 1
            data.loc[index, 'info_tokens_evolution'] = 1
            data.loc[index + 1, 'info_tokens'] = data.loc[index, 'info_tokens'] + 1

    # loose an error token if the card does not fit in and discard it
    else:
        g.error_tokens -= 1
        g.discard_pile.append(c)
        data.loc[index, 'error'] = 1
        data.loc[index + 1, str(c.value) + ' ' + str(c.color) + ' in the discard pile'] = data.loc[index, str(c.value) + ' ' + str(c.color) + ' in the discard pile'] + 1
        data.loc[index + 1, 'error_tokens'] = data.loc[index, 'error_tokens'] - 1
        # discard pile
        data.loc[index + 1, str(c.value) + ' ' + str(c.color) + ' in the discard pile'] += 1
    
    # draw a card if possible
    if len(g.draw_pile) > 0:
        p.deck.append(g.draw_pile[0])
        del g.draw_pile[0]
       
    return data
    

def give_info_neural_network(g, current_player_index, players_number, player_info, info_type, info, data, index):  
    g.info_tokens -= 1
    data.loc[index, 'info_tokens_evolution'] = -1
    data.loc[index + 1, 'info_tokens'] = data.loc[index, 'info_tokens'] - 1

    if info_type == 'color':
        data.loc[index, 'say to player ' + str((g.players.index(player_info) - current_player_index) % players_number) + ' the ' + str(info)] = 1
        for c in player_info.deck:
            if c.color == info:
                c.color_info = info
                
    else:
        data.loc[index, 'say to player ' + str((g.players.index(player_info) - current_player_index) % players_number) + ' the ' + str(info)] = 1
        for c in player_info.deck:
            if c.value == info:
                c.value_info = info
                
    # game information and discard pile
    data.iloc[index + 1, 1:31] = np.array(data.iloc[index, 1:31])
    
    return data
    
    
def check_end_game_neural_network(g, no_draw_pile_counter):
    end_game = False
    
    if len(g.draw_pile) == 0:
        no_draw_pile_counter += 1
    
    if (sum(g.fireworks.values()) == 25) or (no_draw_pile_counter == len(g.players) + 1) or (g.error_tokens == 0):
        end_game = True   
    
    return end_game, no_draw_pile_counter


###############################################################################
# function that initializes the data for neural network at the start of a game
###############################################################################

def data_game_initialization(data, g, first_player, index):
    
    # infos and error tokens
    data.loc[index, 'info_tokens'] = 8
    data.loc[index, 'error_tokens'] = 3
    
    # next players' deck
    for next_turn in range(1, len(g.players)):
        next_player = g.players[(first_player + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        card_index = 0
        for c in next_player_deck:
            data.loc[index, 'player ' + str(next_turn) + ' turn(s) after : card ' + str(card_index) + ' is ' + str(c.color)] = 1
            data.loc[index, 'player ' + str(next_turn) + ' turn(s) after : card ' + str(card_index) + ' is ' + str(c.value)] = 1
            card_index += 1 
    
    return data







