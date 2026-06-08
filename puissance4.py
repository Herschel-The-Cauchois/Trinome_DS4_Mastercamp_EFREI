# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 10:11:07 2026

@author: leste
"""
import copy

COLS=12
LIGNES=6
IA=1
ADV=-1
VIDE=0

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
                self.successors.append(MinMaxTree(self.root_player, "min" if self.state == "max" else "max",Game(succ[i], 0 if self.game.player == 1 else 1), self, [])) # Successor is a node of other state with a game whose turn is for the other player following the possible actions done
                self.successors[i].generate_successors()
        elif self.game.Utility(self.game.player) == None: # Is the game not finished ? elif is necessary because after many test, it executed both conditions at the started and ruined the minimax
            succ = self.game.actions(0 if self.game.player == 1 else 1) # In the successor iterations, the game turns will of course be done by the other player
            for i in range(0, len(succ)): # i iteration used because it's better for recursive successor generation
                self.successors.append(MinMaxTree(self.root_player, "min" if self.state == "max" else "max",Game(succ[i], 0 if self.game.player == 1 else 1), self, [])) # Successor is a node of other state with a game whose turn is for the other player following the possible actions done
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
        
class Game:
    def __init__(self, grid=None, player=IA):
        if grid == None:
            self.grid = [[VIDE for _ in range(COLS)] for _ in range(LIGNES)]
        else:
            self.grid = grid

        self.player = player

    def actions(self, player):
        successors = []
        for col in range(COLS):
            if self.grid[0][col] != VIDE:
                continue
            new_grid = copy.deepcopy(self.grid)
            row = 0
            while row < LIGNES and new_grid[row][col] == VIDE:
                row += 1
            row -= 1
            new_grid[row][col] = player
            successors.append(new_grid)
        return successors

    def Terminal_test(self):
        return self.Utility(IA) is not None
    
    def play(self, player, col):
        row = 0
        while row < LIGNES and self.grid[row][col] == VIDE:
            row += 1
        row -= 1
        self.grid[row][col] = player

    def winner(self):
        g = self.grid
        for r in range(LIGNES):
            for c in range(COLS):
                p = g[r][c]
                if p == VIDE:
                    continue
                # horizontal
                if c <= COLS - 4:
                    if all(g[r][c+i] == p for i in range(4)):
                        return p
                # vertical
                if r <= LIGNES - 4:
                    if all(g[r+i][c] == p for i in range(4)):
                        return p
                # diagonale \
                if r <= LIGNES - 4 and c <= COLS - 4:
                    if all(g[r+i][c+i] == p for i in range(4)):
                        return p
                # diagonale /
                if r >= 3 and c <= COLS - 4:
                    if all(g[r-i][c+i] == p for i in range(4)):
                        return p
        return None

    def Utility(self, root_player):
        winner = self.winner()
        if winner == root_player:
            return 1
        if winner == -root_player:
            return -1
        full = True
        for col in range(COLS):
            if self.grid[0][col] == VIDE:
                full = False
                break
        if full:
            return 0
        return None
    

def print_board(board):
    symbols = {
        IA: "X" ,
        ADV:"0" ,
        VIDE:" "
    }
    print()
    for lignes in board:
        print(" ".join(symbols[cell] for cell in lignes))

        # print(" ".join(str(i % 10) for i in range(COLS)))
    print() 

def IA_Decision(state):
    root_game = Game(state, IA)
    tree = MinMaxTree(
        rootp=IA,
        state="max",
        game=root_game,
        pred=None,
        succ=[]
    )

    tree.generate_successors()

    return tree.minimax_decision()

def Terminal_test(state):
    return False

def main():
    start = int(input("Qui commence ? [1=IA, -1=Humain]: "))
    game = Game()
    current_player = 1 if start == 1 else -1

    while not game.Terminal_test():
        if current_player == 1:
            col = IA_Decision(game.grid)
        else:
            col = int(input("Entrez une colonne [0-11]: "))
        game.play(current_player, col)
        print_board(game.state)
        current_player = 1 if current_player == -1 else -1

        


if __name__ == "__main__":
    main()
       
