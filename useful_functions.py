# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 08:57:59 2019

@author: flelay
"""

# return the best information type regarding the deck and the given card
def info_to_give(d, input_card):
    other_cards = list(filter(lambda x: x not in [input_card], d))
    
    same_color_cards = False
    same_value_cards = False
    
    for c in other_cards:            
        if (c.color == input_card.color) and (c.color_info == ""):
            same_color_cards = True
        
        if (c.value == input_card.value) and (c.value_info == 10):
            same_value_cards = True
        
    if same_color_cards and same_value_cards:
        return 'do not give info'
    elif same_color_cards:
        return 'value'
    else:
        return 'color'


# return True if there is not any other card in the deck with the same value or color
def same_value_or_color_cards(d, input_card):
    other_cards = list(filter(lambda x: x not in [input_card], d))
    
    same_color_cards = False
    same_value_cards = False
    
    for c in other_cards:            
        if (c.color == input_card.color) and (c.color_info == ""):
            same_color_cards = True
        
        if (c.value == input_card.value) and (c.value_info == 10):
            same_value_cards = True
        
    if same_color_cards or same_value_cards:
        return True
    else:
        return False


# return True if the player received an information about this card
def info_given_to_player(p, color, value):
    for c in p.deck:
        if (c.color == color) and (c.value == value):
            if (c.color_info != "") or (c.value_info != 10):
                return True
    return False


# return True if the information has not already be given to someone else
def unseen_information(g, player_info, card_info, info_type):
    informed_cards = []
    
    for c in player_info.deck:
        if info_type == 'color':
            if c.color == card_info.color:
                informed_cards.append(c)
        else:
            if c.value == card_info.value:
                informed_cards.append(c)
                
    for c in informed_cards:
        for p in g.players:
            for card_to_check in p.deck:
                if (card_to_check.color == c.color) and (card_to_check.value == c.value):
                    if (card_to_check.color_info != "") or (card_to_check.value_info != 10):
                        return False

    return True


# return True if the player has already too much information about his deck (on 2 cards or more)
def too_much_information(d):
    informed_cards_counter = 0
    
    for c in d:
        if (c.value_info != 10) or (c.color_info != ""):
            informed_cards_counter += 1

    return (informed_cards_counter >= 3)


# return True if the player has an information about a card on the left of the input card (with its value - 1)
def info_on_the_left(d, input_card):
    for c in d:
        if (c.value_info != 10) or (c.color_info != ""):
            return True
        if (c.value == input_card.value - 1) and (c.color == input_card.color):
            return False


# return the value to announce to a player who has several playable cards with the same value, or 0 if not
# return 0 if the 2 cards are of the same color
def several_playable_cards(g, player_info_deck):
    playable_cards = []
    
    for c in player_info_deck:
        if (c.value == g.fireworks[c.color] + 1) and (c.value_info == 10) and (c.color_info == ""):
            playable_cards.append(c)
    
    colors = []
    for c in playable_cards:
        colors.append(c.color)
        
    if len(set(colors)) < len(colors):
        return 0
    
    values_cards = []
    for c in playable_cards:
        values_cards.append(c.value)

    for value in range(1, 6):
        if values_cards.count(value) > 1:
            return value

    return 0


# return True if the player has twice the card in parameter in his/her deck
# AND if both cards have not any information (works also with 3 identical cards)
def duplicated_card(g, player_deck, card):
    other_cards = list(filter(lambda x: x not in [card], player_deck))
    
    for c in other_cards:
        if (c.value == card.value) and (c.color == card.color):
            return True
        
    return False


# return True if the color can not be completed any more (considering the discard pile)
def color_lost(g, color):
    if g.fireworks[color] == 0:
        ones_number = 0
        
        for c in g.discard_pile:
            if (c.value == 1) and (c.color == color):
                ones_number += 1
                
        if ones_number == 3:
            return True
        
    elif g.fireworks[color] == 5:
        return True
    
    else:
        cards_number = 0
        
        for c in g.discard_pile:
            if (c.value == g.fireworks[color] + 1) and (c.color == color):
                cards_number += 1
        
        if cards_number == 2:
            return True
        
    return False



















