# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 10:11:07 2026

@author: leste
"""

# puissance 4

class MinMaxTree:
    def __init__(self, rootp, state = "max", game=None, pred=None, succ = []):
        self.game = game
        self.predecessor = pred
        self.successors = succ # List containing MinMaxTree nodes
        self.state = state # variable to indicate whether this should be min or max in the algorithm steps
        self.value = None # Default value, to be determined when running min value or max value
        self.root_player = rootp # Necessary when we need to calculate the utility for the player at the root tree
        
    def generate_successors(self):
        if self.predecessor == None: # Root node case
            succ = self.game.actions(self.root_player) # In the successor iterations, the game turns will of course be done by the other player
            for i in range(0, len(succ)): # i iteration used because it's better for recursive successor generation
                self.successors.append(MinMaxTree(self.root_player, "min" if self.state == "max" else "max",Morpion(succ[i], 0 if self.game.player == 1 else 1), self, [])) # Successor is a node of other state with a game whose turn is for the other player following the possible actions done
                self.successors[i].generate_successors()
        elif self.game.Utility(self.game.player) == None: # Is the game not finished ? elif is necessary because after many test, it executed both conditions at the started and ruined the minimax
            succ = self.game.actions(0 if self.game.player == 1 else 1) # In the successor iterations, the game turns will of course be done by the other player
            for i in range(0, len(succ)): # i iteration used because it's better for recursive successor generation
                self.successors.append(MinMaxTree(self.root_player, "min" if self.state == "max" else "max",Morpion(succ[i], 0 if self.game.player == 1 else 1), self, [])) # Successor is a node of other state with a game whose turn is for the other player following the possible actions done
                self.successors[i].generate_successors()
                
    def max_value(self, alpha = None, beta = None): # if one of alpha or beta is missing, classic minimax mode
        if self.game.Utility(0) != None: # Is the game finished ?
            self.value = self.game.Utility(self.root_player)
            return self.value
        self.value = float("-inf")
        for i in range(0, len(self.successors)):
            self.value = max(self.value, self.successors[i].min_value())
            if alpha != None and beta != None:
                if self.value <= alpha:
                    return self.value
                alpha = max(alpha, self.value)
                print("alpha : "+ str(alpha))
        return self.value
    
    def min_value(self, alpha = None, beta = None): # if one of alpha or beta is missing, classic minimax mode
        if self.game.Utility(0) != None: # Is the game finished ?
            self.value = self.game.Utility(self.root_player)
            return self.value
        self.value = float("inf")
        for i in range(0, len(self.successors)):
            self.value = min(self.value, self.successors[i].max_value())
            if alpha != None and beta != None:
                if self.value <= alpha:
                    return self.value
                beta = min(beta, self.value)
                print("beta : " + str(beta))
        return self.value
    
    def minimax_decision(self, isAlphaBeta):
        decision_index = 0
        if isAlphaBeta:
            for i in range(0, len(self.successors)):
                print(self.successors[decision_index].value)
                if i == 0:
                    self.successors[i].MinVal(self.alpha, self.beta)
                elif self.successors[decision_index].value < self.successors[i].MinVal(self.alpha, self.beta):
                    decision_index = i
            return self.successors[decision_index].game.grid # returns grid of next action to take by player x
        else:
            for i in range(0, len(self.successors)):
                print(self.successors[decision_index].value)
                if i == 0:
                    self.successors[i].MinVal()
                elif self.successors[decision_index].value < self.successors[i].MinVal():
                    decision_index = i
            return self.successors[decision_index].game.grid # returns grid of next action to take by player x