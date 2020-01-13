# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 10:01:09 2019

@author: flelay
"""

from random import shuffle
from colorama import Fore, Style

class card:
    def __init__(self, color, value):
        self.color = color
        self.value = value
        self.color_info = ""
        self.value_info = 10
        
    def __str__(self):
        if self.color == 'blue':
            print(Fore.BLUE + Style.BRIGHT, self.value, sep = "", end = "" + Style.RESET_ALL)
        elif self.color == 'red':
            print(Fore.RED + Style.BRIGHT, self.value, sep = "", end = "" + Style.RESET_ALL)
        elif self.color == 'green':
            print(Fore.GREEN + Style.BRIGHT, self.value, sep = "", end = "" + Style.RESET_ALL)
        elif self.color == 'yellow':
            print(Fore.YELLOW + Style.BRIGHT, self.value, sep = "", end = "" + Style.RESET_ALL)
        else:
            print(Fore.WHITE + Style.BRIGHT, self.value, sep = "", end = "" + Style.RESET_ALL)        
        return("")


class player:
    def __init__(self, dna, deck = []):
        self.dna = dna
        self.deck = deck

    def __str__(self):
        print("| ", end = "")
        for c in self.deck:
            print(c, end = "")
            if (c.value_info != 10) and (c.color_info != ""):
                print("(", c.value_info, ")", sep = "", end = "")
                print("(", c.color_info[0], ") ", sep = "", end = "")
            elif (c.value_info != 10) and (c.color_info == ""):
                print("(", c.value_info, ")    ", sep = "", end = "")    
            elif (c.value_info == 10) and (c.color_info != ""):
                print("(", c.color_info[0], ")    ", sep = "", end = "")
            else:
                print("       ", end = "")
            print("| ", end = "")
        return("")
        
        
class game:
    def __init__(self):
        self.fireworks = {'blue' : 0, 'red' : 0, 'green' : 0, 'yellow' : 0, 'white' : 0}
        self.players = []
        self.draw_pile = create_draw_pile()
        self.discard_pile = []  
        self.info_tokens = 8
        self.error_tokens = 3
        
    def __str__(self):
        print("Fireworks :")
        print("[  ", Fore.BLUE + Style.BRIGHT, self.fireworks['blue'], "  ",
                Fore.RED + Style.BRIGHT, self.fireworks['red'], "  ", 
                Fore.GREEN + Style.BRIGHT, self.fireworks['green'], "  ", 
                Fore.YELLOW + Style.BRIGHT, self.fireworks['yellow'], "  ", 
                Fore.WHITE + Style.BRIGHT, self.fireworks['white'], "  ", 
                "]", sep = "", end = "" + Style.RESET_ALL)
        print("  [score : ", sum(self.fireworks.values()),"]", sep = "")    
        print("")   
        print("Info tokens :", self.info_tokens)
        print("")
        print("Error tokens :", self.error_tokens)
        print("")
        print("Players decks :")
        for p in self.players:
            print(p)
            print("")
        print("Discard pile :")
        print("|", end = "")
        for c in self.discard_pile:
            print(c, "|", sep = "", end = "")
        print("")
        print("")
        print("Draw pile :")
        print("|", end = "")
        for c in self.draw_pile:
            print(c, "|", sep = "", end = "")
        return("")  
    
    def deal_cards(self, players_number, dna = list(range(1, 21))):
        for i in range(players_number):
            self.players.append(player(dna, self.draw_pile[0:4]))
            del self.draw_pile[0:4]
            

# create the draw pile and shuffle it
def create_draw_pile():
    
    draw_pile = []
    card_list_per_colour = [1, 1, 1, 2, 2 ,3, 3, 4, 4, 5]     
        
    for i in card_list_per_colour:
        draw_pile.append(card("blue", i))
    
    for i in card_list_per_colour:
        draw_pile.append(card("red", i))
        
    for i in card_list_per_colour:
        draw_pile.append(card("green", i))

    for i in card_list_per_colour:
        draw_pile.append(card("yellow", i))
        
    for i in card_list_per_colour:
        draw_pile.append(card("white", i))  
    
    for n in range(5):
        shuffle(draw_pile)
    
    return draw_pile







































