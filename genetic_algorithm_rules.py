# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 14:51:08 2019

@author: flelay
"""

import numpy as np
import pandas as pd
from random import randrange, shuffle, random, choice

from classes import game
from game_functions import play_card, discard, give_info, check_end_game
from useful_functions import info_to_give, info_given_to_player, unseen_information, several_playable_cards, color_lost


###############################################################################
########## genetic algorithm's function #######################################
###############################################################################

# create the population
def create_population(games_number):
    genomes = np.zeros(shape = (games_number, 20)).astype(int)
    players_basic_dna = list(range(1, 21))
    
    for i in range(len(genomes)):
        shuffle(players_basic_dna)
        genomes[i] = players_basic_dna
    
    return genomes

# select the best games (future parents)
def select_parents(genomes, players_number, repetitions):
    scores = [0] * len(genomes)
    
    for i in range(len(genomes)):
        mean_score = 0
        for n in range(repetitions):
            g = game()    
            g.deal_cards(players_number, genomes[i])
            g, score, lost = launch_game_genetic(g, False)
            mean_score += score
        mean_score /= repetitions
        
        scores[i] = mean_score

    parents_genomes = genomes[np.argpartition(scores, int(-len(genomes)/2))[int(-len(genomes)/2):]]

    return parents_genomes

# generate children from parents
def generate_children(parents_genomes, children_number):
    parents_counter = 0
    children_genomes = np.zeros(shape = (children_number, 20))
    
    for i in range(children_number):
        # select parents
        parent_1 = parents_genomes[parents_counter % len(parents_genomes)]
        parent_2 = parents_genomes[(parents_counter + 1) % len(parents_genomes)]
        parents_counter += 1
        
        # crossover between parents' genomes
        alleles_list = pd.DataFrame(columns = list(range(1, 21)))
        for gene in range(1, 21):
            allele_parent_1 = np.take(np.where(parent_1 == gene), 0)
            allele_parent_2 = np.take(np.where(parent_2 == gene), 0)
            alleles_list.loc[0, gene] = (allele_parent_1 + allele_parent_2) / 2
        alleles_list.sort_values(by = 0, axis = 1, inplace = True)
        children_genomes[i] = alleles_list.columns
        
        # add mutation with a given probability
        if random() < 0.3:
            gene_1 = choice(range(20))
            gene_2 = choice(range(20))
            children_genomes[i][gene_1], children_genomes[i][gene_2] = children_genomes[i][gene_2], children_genomes[i][gene_1]
    
    children_genomes = children_genomes.astype(int)
    
    # add parents_genomes
    children_genomes = np.concatenate((children_genomes, parents_genomes))
    np.random.shuffle(children_genomes)
        
    return children_genomes
        
# evaluate a generation of players
def evaluate_generation(genomes, players_number, repetitions):

    generation_score = 0
    for i in range(len(genomes)):
        for n in range(repetitions):
            g = game()    
            g.deal_cards(players_number, genomes[i])
            g, score, lost = launch_game_genetic(g, False)
            generation_score += score
    generation_score /= (repetitions * len(genomes))
    
    return generation_score

def genetic_algorithm(players_number, games_number, repetitions, children_number, generations_number):
#    genomes = create_population(games_number)
    genomes = np.zeros(shape = (games_number, 20)).astype(int)
    for i in range(len(genomes)):
        genomes[i] = list(range(1, 21))
        for n in range(5):
            gene_1 = choice(range(20))
            gene_2 = choice(range(20))
            genomes[i][gene_1], genomes[i][gene_2] = genomes[i][gene_2], genomes[i][gene_1]
    
    generation_score = evaluate_generation(genomes, players_number, repetitions)
    scores = [generation_score]
    print("score initial generation :", generation_score)
    
    for n in range(generations_number):
        parents_genomes = select_parents(genomes, players_number, repetitions)
        children_genomes = generate_children(parents_genomes, children_number)
        generation_score = evaluate_generation(children_genomes, players_number, repetitions)
        scores += [generation_score]
        print("score generation", n + 1 , ":", generation_score)

    last_generation_genomes = children_genomes
    print("last_generation_genomes :")
    print(last_generation_genomes)
    
    return scores, last_generation_genomes
    
###############################################################################
########## game main function for the genetic algorithm #######################
###############################################################################
    
def launch_game_genetic(g, display):
    
    first_player = randrange(len(g.players))
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
        turn_player_genetic(g, g.players[current_player])
        if display:
            turn_number += 1
            if turn_number < 100:
                print(g)
                print("")
                print("turn_number :", turn_number)
                print("current player :", current_player)
                print("__________________________________________________________")
        end_game, no_draw_pile_counter = check_end_game(g, no_draw_pile_counter)
        
        current_player = (current_player + 1) % len(g.players)
       
    # Results display
    if g.error_tokens == 0:
        lost = True
        if display:
            print("game lost")
    else:
        lost = False
    
    return g, sum(g.fireworks.values()), lost

###############################################################################
########## turn function based on the dna of the player #######################
###############################################################################

def turn_player_genetic(g, p):
    
    for gene in p.dna:
        action_done = globals()['choice_' + str(gene)](g, p)
        if action_done:
            return
    
###############################################################################
########## choice functions ###################################################
###############################################################################

def choice_1(g, p):
    for c in p.deck:
        if (c.color_info != "") and (c.value_info != 10):
            if c.value_info <= g.fireworks[c.color_info]:
                discard(g, p, c)
                return True
            else:
                play_card(g, p, c)
                return True
        elif c.color_info != "":
            if (g.fireworks[c.color_info] == 5) or (color_lost(g, c.color)):
                discard(g, p, c)
                return True
            else:
                play_card(g, p, c)
                return True
        elif c.value_info != 10:
            if (c.value_info < 5) and (c.value_info <= min(g.fireworks.values())):
                discard(g, p, c)
                return True
            elif c.value_info < 5:
                play_card(g, p, c)
                return True
    return False


def choice_2(g, p):
    if g.info_tokens >= 1:
        next_turn = 1
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        recurrent_value = several_playable_cards(g, next_player_deck)
        if recurrent_value != 0:
            good_info = True
            for c in next_player_deck:
                if (c.value == recurrent_value) and (c.color_info == "") and (c.value_info == 10):
                    if (not(unseen_information(g, next_player, c, 'value'))) or (not(unseen_information(g, next_player, c, 'color'))) or (c.value < g.fireworks[c.color] + 1):
                        good_info = False
            if good_info:
                give_info(g, next_player, 'value', recurrent_value)
                return True
    return False


def choice_3(g, p):
    if g.info_tokens >= 1:
        next_turn = 2
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        recurrent_value = several_playable_cards(g, next_player_deck)
        if recurrent_value != 0:
            good_info = True
            for c in next_player_deck:
                if (c.value == recurrent_value) and (c.color_info == "") and (c.value_info == 10):
                    if (not(unseen_information(g, next_player, c, 'value'))) or (not(unseen_information(g, next_player, c, 'color'))) or (c.value < g.fireworks[c.color] + 1):
                        good_info = False
            if good_info:
                give_info(g, next_player, 'value', recurrent_value)
                return True
    return False


def choice_4(g, p):
    if g.info_tokens >= 1:
        next_turn = 1
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck: 
            if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                info = info_to_give(next_player_deck, c)
                if info == "color":
                    if unseen_information(g, next_player, c, 'color'):
                        give_info(g, next_player, 'color', c.color)
                        return True
                elif info == "value":
                    if unseen_information(g, next_player, c, 'value'):
                        give_info(g, next_player, 'value', c.value)
                        return True
    return False


def choice_5(g, p):
    if g.info_tokens >= 1:
        next_turn = 2
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck: 
            if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                info = info_to_give(next_player_deck, c)
                if info == "color":
                    if unseen_information(g, next_player, c, 'color'):
                        give_info(g, next_player, 'color', c.color)
                        return True
                elif info == "value":
                    if unseen_information(g, next_player, c, 'value'):
                        give_info(g, next_player, 'value', c.value)
                        return True
    return False


def choice_6(g, p):
    if g.info_tokens >= 1:
        next_turn = 2
        player_before_next = g.players[(g.players.index(p) + next_turn - 1) % len(g.players)]
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value == g.fireworks[c.color] + 2) and (c.color_info == "") and (c.value_info == 10) and info_given_to_player(player_before_next, c.color, g.fireworks[c.color] + 1):
                info = info_to_give(next_player_deck, c)
                if info == "color":
                    if unseen_information(g, next_player, c, 'color'):
                        give_info(g, next_player, 'color', c.color)
                        return True
                elif info == "value":
                    if unseen_information(g, next_player, c, 'value'):
                        give_info(g, next_player, 'value', c.value)
                        return True
    return False


def choice_7(g, p):
    if g.info_tokens >= 1:
        next_turn = 3
        player_before_next = g.players[(g.players.index(p) + next_turn - 1) % len(g.players)]
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value == g.fireworks[c.color] + 2) and (c.color_info == "") and (c.value_info == 10) and info_given_to_player(player_before_next, c.color, g.fireworks[c.color] + 1):
                info = info_to_give(next_player_deck, c)
                if info == "color":
                    if unseen_information(g, next_player, c, 'color'):
                        give_info(g, next_player, 'color', c.color)
                        return True
                elif info == "value":
                    if unseen_information(g, next_player, c, 'value'):
                        give_info(g, next_player, 'value', c.value)
                        return True
    return False


def choice_8(g, p):
    if g.info_tokens >= 1:
        next_turn = 1
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                give_info(g, next_player, 'value', 5)
                return True
            elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                give_info(g, next_player, 'value', c.value)
                return True
            elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                give_info(g, next_player, 'color', c.color)
                return True
    return False


def choice_9(g, p):
    if g.info_tokens >= 1:
        next_turn = 2
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                give_info(g, next_player, 'value', 5)
                return True
            elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                give_info(g, next_player, 'value', c.value)
                return True
            elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                give_info(g, next_player, 'color', c.color)
                return True
    return False


def choice_10(g, p):
    if g.info_tokens >= 1:
        next_turn = 3
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                info = info_to_give(next_player_deck, c)
                if info == "color":
                    if unseen_information(g, next_player, c, 'color'):
                        give_info(g, next_player, 'color', c.color)
                        return True
                elif info == "value":
                    if unseen_information(g, next_player, c, 'value'):
                        give_info(g, next_player, 'value', c.value)
                        return True
    return False


def choice_11(g, p):
    if g.info_tokens >= 1:
        for next_turn in range(4, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value == g.fireworks[c.color] + 1) and (c.color_info == "") and (c.value_info == 10):
                    info = info_to_give(next_player_deck, c)
                    if info == "color":
                        if unseen_information(g, next_player, c, 'color'):
                            give_info(g, next_player, 'color', c.color)
                            return True
                    elif info == "value":
                        if unseen_information(g, next_player, c, 'value'):
                            give_info(g, next_player, 'value', c.value)
                            return True
    return False


def choice_12(g, p):
    if g.info_tokens >= 1:
        next_turn = 3
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                give_info(g, next_player, 'value', 5)
                return True
            elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                give_info(g, next_player, 'value', c.value)
                return True
            elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                give_info(g, next_player, 'color', c.color)
                return True
    return False


def choice_13(g, p):
    if g.info_tokens >= 1:
        for next_turn in range(4, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value == 5) and (c.color_info == "") and (c.value_info == 10):
                    give_info(g, next_player, 'value', 5)
                    return True
                elif (min(g.fireworks.values()) >= c.value) and (c.value_info == 10):
                    give_info(g, next_player, 'value', c.value)
                    return True
                elif (g.fireworks[c.color] == 5) and (c.color_info == ""):
                    give_info(g, next_player, 'color', c.color)
                    return True
    return False


def choice_14(g, p):
    if g.info_tokens >= 1:
        next_turn = 1
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value_info == 5) and (c.color_info == "") and (g.fireworks[c.color] == 4):
                give_info(g, next_player, 'color', c.color)
                return True
    return False


def choice_15(g, p):
    if g.info_tokens >= 1:
        next_turn = 2
        next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
        next_player_deck = next_player.deck
        for c in next_player_deck:
            if (c.value_info == 5) and (c.color_info == "") and (g.fireworks[c.color] == 4):
                give_info(g, next_player, 'color', c.color)
                return True
    return False


def choice_16(g, p):
    if (len(g.draw_pile) < 4) and g.error_tokens >= 2:
        for c in p.deck:
            if (c.color_info == "") and (c.value_info == 10):
                play_card(g, p, c)
                return True
    return False


def choice_17(g, p):
    if g.info_tokens < 8:
        for c in p.deck:
            if c.value_info != 5:
                discard(g, p, c)
                return True
    return False


def choice_18(g, p):
    if g.info_tokens >= 1:
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    if info_to_give(next_player_deck, c) == 'color':
                        give_info(g, next_player, 'color', c.color)
                        return True
                    
        for next_turn in [1, 2]:
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    give_info(g, next_player, 'color', c.color)
                    return True
    return False


def choice_19(g, p):
    if g.info_tokens >= 1:
        for next_turn in range(3, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    if info_to_give(next_player_deck, c) == 'color':
                        give_info(g, next_player, 'color', c.color)
                        return True
                    
        for next_turn in range(3, len(g.players)):
            next_player = g.players[(g.players.index(p) + next_turn) % len(g.players)]
            next_player_deck = next_player.deck
            for c in next_player_deck:
                if (c.value_info == 5) and (c.color_info == ""):
                    give_info(g, next_player, 'color', c.color)
                    return True
    return False


def choice_20(g, p):
    for c in p.deck:
        if (c.color_info == "") and (c.value_info == 10):
            play_card(g, p, c)
            return True
    for c in p.deck:
        if (c.color_info == "") and (c.value_info != 5):
            play_card(g, p, c)
            return True
    for c in p.deck:
        if (c.color_info == "") or (c.value_info != 10):
            play_card(g, p, c)
            return True
    return False






















