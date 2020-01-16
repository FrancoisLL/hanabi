# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 11:19:48 2019

@author: flelay
"""

from random import randrange, choice
from copy import deepcopy

from classes import game
from game_functions import play_card, discard, give_info, check_end_game
from useful_functions import info_to_give, info_given_to_player, unseen_information, several_playable_cards, color_lost, duplicated_card, too_much_information, info_on_the_left, same_value_or_color_cards


###############################################################################
########## choice functions ###################################################
###############################################################################

def turn_player(g, p):
    
#    # choose an action randomly
#    random_choice(g, p)
    
    # use simple rules to make the decisions
    simple_rules(g, p)

def random_choice(g, p):
    # choice 0 : discard
    # choice 1 : play a card
    # choice 2 : give info
    possible_choices = [0, 1, 2]
    
    # can not discard if there are already 8 info tokens
    if g.info_tokens == 8:
        possible_choices.remove(0)
    # can not give info if there are not any info token left
    elif g.info_tokens == 0:
        possible_choices.remove(2)
    
    action_choice = choice(possible_choices)
    
    if action_choice == 0:
        # choose randomly the card to discard
        discarded_card = randrange(len(p.deck))
        discard(g, p, p.deck[discarded_card])
    
    elif action_choice == 1:
        # choose randomly the card to play
        played_card = randrange(len(p.deck))
        play_card(g, p, p.deck[played_card])
        
    else:
        # choose randomly the player to give information
        p_index = g.players.index(p)
        other_players_index = list(range(len(g.players)))
        other_players_index.remove(p_index)
        player_info = g.players[choice(other_players_index)]
        
        # choose randomly the card to give information on
        card_info = randrange(len(player_info.deck))
        
        # choose randomly the type of information : 0 for color, 1 for value
        info_type = choice(['color', 'value'])
        
        if info_type == 'color':
            info = choice(['blue', 'red', 'green', 'yellow', 'white']) 
        else:
            info = randrange(1, 6)
        
        give_info(g, player_info, card_info, info_type, info)


###############################################################################

# use simple rules to make the decisions
def simple_rules(g, p):
    # play a card if the information on it is known and can be played
    # discard it if the card is useless
    for c in p.deck:
        if (c.color_info != "") and (c.value_info != 10):
            if c.value == g.fireworks[c.color_info] + 1:
                play_card(g, p, c)
                return
    for c in p.deck:
        if (c.color_info != "") and (c.value_info != 10):
            if c.value_info <= g.fireworks[c.color_info]:
                discard(g, p, c)
                return
            elif c.value_info == g.fireworks[c.color_info] + 1:
                play_card(g, p, c)
                return
        elif c.color_info != "":
            if (g.fireworks[c.color_info] == 5) or (color_lost(g, c.color)):
                discard(g, p, c)
                return
            else:
                play_card(g, p, c)
                return
        elif c.value_info != 10:
            if (c.value_info < 5) and (c.value_info <= min(g.fireworks.values())):
                discard(g, p, c)
                return
            elif (c.value_info < 5) and (c.value_info <= max(g.fireworks.values()) + 1):
                play_card(g, p, c)
                return
                
    # give the information if a player among the 2 nexts has 2 playable cards
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                recurrent_value = several_playable_cards(g, next_player_deck)
                if recurrent_value != 0:
                    good_info = True
                    for c in next_player_deck:
                        if (c.value == recurrent_value) and (c.color_info == "") and (c.value_info == 10):
                            if (not(unseen_information(g, next_player, c, 'value'))) or (not(unseen_information(g, next_player, c, 'color'))) or (c.value < g.fireworks[c.color] + 1):
                                good_info = False
                    if good_info:
                        give_info(g, next_player, 'value', recurrent_value)
                        return  
    
    # complete the information about a "5" of the 2 next players if it is playable
    if g.info_tokens >= 1:
        for next_turn in range(1, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == "") and (g.fireworks[c.color] == 4):
                    same_color_cards = 0
                    for cards in next_player_deck:
                        if cards.color == c.color:
                            same_color_cards += 1
                    if same_color_cards <= 1:
                        give_info(g, next_player, 'color', c.color)
                        return    
    
    # give an information if the 2 next players have nice cards with not any info on it
    # and if there is at least an info token left
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck: 
                    if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                        info = info_to_give(next_player_deck, c)
                        if info == "color":
                            if unseen_information(g, next_player, c, 'color'):
                                give_info(g, next_player, 'color', c.color)
                                return
                        elif info == "value":
                            if unseen_information(g, next_player, c, 'value'):
                                give_info(g, next_player, 'value', c.value)
                                return
                    
    # give an information to a player if the previous player has an information so the second one
    # will be able to play a card just after (second and third next players)
    if g.info_tokens >= 1:
        for next_turn in [2, 3]:
            player_before_next = g.players[(g.players.index(p) + next_turn - 1) % len(g.players)]
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck:
                    if (c.value == g.fireworks[c.color] + 2) and (c.color_info == "") and (c.value_info == 10) and info_given_to_player(player_before_next, c.color, g.fireworks[c.color] + 1) and not(info_on_the_left(player_before_next.deck, c)):
                        info = info_to_give(next_player_deck, c)
                        if info == "color":
                            if unseen_information(g, next_player, c, 'color'):
                                give_info(g, next_player, 'color', c.color)
                                return
                        elif info == "value":
                            if unseen_information(g, next_player, c, 'value'):
                                give_info(g, next_player, 'value', c.value)
                                return  
                
    # give an information about a "5" or a useless card in the 2 next players' deck
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck:
                    if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                        give_info(g, next_player, 'value', 5)
                        return
                    elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                        give_info(g, next_player, 'value', c.value)
                        return
                    elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                        give_info(g, next_player, 'color', c.color)
                        return    
            
    # give an information if the next players have nice cards with not any info on it
    # and if there is at least an info token left (from the third next player)
    if g.info_tokens >= 1:
        for next_turn in range(3, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck:
                    if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                        info = info_to_give(next_player_deck, c)
                        if info == "color":
                            if unseen_information(g, next_player, c, 'color'):
                                give_info(g, next_player, 'color', c.color)
                                return
                        elif info == "value":
                            if unseen_information(g, next_player, c, 'value'):
                                give_info(g, next_player, 'value', c.value)
                                return  
    
    # give an information about a "5" or a useless card in the next players' deck (from the third next player)
    if g.info_tokens >= 1:
        for next_turn in range(3, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck:
                    if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                        give_info(g, next_player, 'value', 5)
                        return
                    elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                        give_info(g, next_player, 'value', c.value)
                        return
                    elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                        give_info(g, next_player, 'color', c.color)
                        return
    
    # complete the information about a "5" of the next players
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == "") and (g.fireworks[c.color] == 4) and not(same_value_or_color_cards(next_player_deck, c)):
                    give_info(g, next_player, 'color', c.color)
                    return
    
    # complete the information about an unplayable informed card
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck            
            for c in next_player_deck:
                if (c.value_info == 10) and (c.color_info != ""):
                    if c.value != g.fireworks[c.color] + 1:
                        info = info_to_give(next_player_deck, c)
                        if info == "value":
                            give_info(g, next_player, 'value', c.color)
                            return 
                if (c.value_info != 10) and (c.color_info == ""):
                    if c.value != g.fireworks[c.color] + 1:
                        info = info_to_give(next_player_deck, c)
                        if info == "color":
                            give_info(g, next_player, 'color', c.color)
                            return

    # throw a card (not a "5") if it is not useful in a near future
    if g.info_tokens < 8:
        for c in p.deck:
            if (c.value_info != 10) and (c.value != 5):
                if c.value_info > max(g.fireworks.values()) + 1:
                    discard(g, p, c)
                    return
    
    # throw a random card (not a useful "5") if no information about the deck
    if g.info_tokens < 6:
        for c in p.deck:
            if c.value_info != 5:
                discard(g, p, c)
                return
    
    # complete the information about a "5" with no cards with the same color in the deck to not discard randomly
    if g.info_tokens >= 1:
        for next_turn in range(1, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    if not(same_value_or_color_cards(next_player_deck, c)):
                        give_info(g, next_player, 'color', c.color)
                        return
    
    # complete the color information about cards that are the same and with the value only as information
    if g.info_tokens >= 1:
        for next_turn in range(1, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (duplicated_card(g, next_player_deck, c)) and (c.value <= g.fireworks[c.color]) and (c.value_info != 10) and (c.color_info == "") and not(same_value_or_color_cards(next_player_deck, c)):
                    give_info(g, next_player, 'color', c.color)
                    return
    
    # give an information about a playable card which appears twice in the deck of one of the next players
    if g.info_tokens >= 1:
        for next_turn in range(1, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck:
                    if (duplicated_card(g, next_player_deck, c)) and (c.value == g.fireworks[c.color] + 1) and (c.value_info == 10) and (c.color_info == ""):
                        give_info(g, next_player, 'value', c.value)
                        return                    

    # give an information about a playable card but with cards with same color and same value in the deck
    # can not be given to the player just after
    if g.info_tokens >= 1:
        for next_turn in range(2, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            if not(too_much_information(next_player_deck)):
                for c in next_player_deck:
                    if (c.value_info == 10) and (c.color_info == "") and (c.value == g.fireworks[c.color] + 1):
                        give_info(g, next_player, 'value', c.value)
                        return
            
    # give a random information if there are a lot of info tokens instead of playing a random card
    # priority for the "4" when the game is near of its start
    if g.info_tokens >= 6:
        for next_turn in range(3, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info != 10) and (c.color_info == "") and (c.value == 4) and (max(g.fireworks.values()) < 3):
                    give_info(g, next_player, 'value', 4)
                    return
            for c in next_player_deck:
                info = info_to_give(next_player_deck, c)
                if (c.value_info != 10) and (c.color_info == "") and (info == 'color'):
                    give_info(g, next_player, 'color', c.color)
                    return
                if (c.value_info == 10) and (c.color_info != "") and (info == 'value'):
                    give_info(g, next_player, 'value', c.value)
                    return
                    
    # try to put a random card if the game is almost done and there are still error tokens
    if (len(g.draw_pile) < 4) and g.error_tokens >= 2:
        for c in p.deck:
            if (c.color_info == "") and (c.value_info == 10):
                play_card(g, p, c)
                return            
                
    # throw a random card (not a known useful "5") if no information about the deck
    if g.info_tokens < 8:
        for c in p.deck:
            if c.value_info != 5:
                discard(g, p, c)
                return
            
    # play a random card (rarely happens)
    for c in p.deck:
        if (c.color_info == "") and (c.value_info == 10):
            play_card(g, p, c)
            return
    for c in p.deck:
        if (c.color_info == "") and (c.value_info != 5):
            play_card(g, p, c)
            return
    for c in p.deck:
        if (c.color_info == "") or (c.value_info != 10):
            play_card(g, p, c)
            return
        
    
###############################################################################
########## game main function #################################################
###############################################################################
    
def launch_game(players_number, display):
    # use a constant seed for the tests
    #seed(123)
    g = game()
    g.deal_cards(players_number)
    
    first_player = randrange(players_number)
    current_player = first_player
    
    end_game = False
    no_draw_pile_counter = 0
    if display:
        turn_number = 0
        print(g)
        print("turn number :", turn_number)
        print("first player :", first_player)
        print("__________________________________________________________")
    
    while not(end_game):
        turn_player(g, g.players[current_player])
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
    
    return g, sum(g.fireworks.values()), lost, g.error_tokens

    
# game main function with a save at each turn
def saved_launch_game(players_number, display):
    g = game()
    g.deal_cards(players_number)
    data_game = [deepcopy(g)]
    
    first_player = randrange(players_number)
    current_player = first_player
    
    end_game = False
    no_draw_pile_counter = 0
    if display:
        turn_number = 0
        print(g)
        print("turn number :", turn_number)
        print("first player :", first_player)
        print("__________________________________________________________")
    
    while not(end_game):
        turn_player(g, g.players[current_player])
        data_game += [deepcopy(g)]
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
    
    return data_game, first_player, sum(g.fireworks.values()), lost       
        
        
        
        
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    