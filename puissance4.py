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

    def __init__(
        self,
        rootp,
        state="max",
        game=None,
        pred=None,
        move=None
    ):
        self.game = game
        self.predecessor = pred
        self.successors = []
        self.state = state
        self.value = None
        self.root_player = rootp
        self.move = move

    def generate_successors(self, depth):

        if depth == 0:
            return

        if self.game.Utility(self.root_player) is not None:
            return

        player_to_play = self.game.player

        for col in self.game.actions():

            child_game = self.game.result(col, player_to_play)

            child = MinMaxTree(
                self.root_player,
                "min" if self.state == "max" else "max",
                child_game,
                self,
                col
            )

            self.successors.append(child)

            child.generate_successors(depth - 1)

    def max_value(self):

        util = self.game.Utility(self.root_player)

        if util is not None:
            self.value = util
            return util

        if not self.successors:
            return 0

        self.value = float("-inf")

        for child in self.successors:
            self.value = max(
                self.value,
                child.min_value()
            )

        return self.value

    def min_value(self):

        util = self.game.Utility(self.root_player)

        if util is not None:
            self.value = util
            return util

        if not self.successors:
            return 0

        self.value = float("inf")

        for child in self.successors:
            self.value = min(
                self.value,
                child.max_value()
            )

        return self.value

    def minimax_decision(self):

        best_move = None
        best_value = float("-inf")

        for child in self.successors:

            value = child.min_value()

            if value > best_value:
                best_value = value
                best_move = child.move

        return best_move
    

class Game:

    def __init__(self, grid=None, player=IA):

        if grid is None:
            self.grid = [
                [VIDE for _ in range(COLS)]
                for _ in range(LIGNES)
            ]
        else:
            self.grid = grid

        self.player = player

    def actions(self):

        actions = []

        for col in range(COLS):

            if self.grid[0][col] == VIDE:
                actions.append(col)

        return actions

    def result(self, col, player):

        new_grid = copy.deepcopy(self.grid)

        row = 0

        while row < LIGNES and new_grid[row][col] == VIDE:
            row += 1

        row -= 1

        new_grid[row][col] = player

        return Game(
            new_grid,
            -player
        )

    def play(self, player, col):

        row = 0

        while row < LIGNES and self.grid[row][col] == VIDE:
            row += 1

        row -= 1

        self.grid[row][col] = player

        self.player = -player

    def winner(self):

        g = self.grid

        for r in range(LIGNES):
            for c in range(COLS):

                p = g[r][c]

                if p == VIDE:
                    continue

                if c <= COLS - 4:
                    if all(g[r][c+i] == p for i in range(4)):
                        return p

                if r <= LIGNES - 4:
                    if all(g[r+i][c] == p for i in range(4)):
                        return p

                if r <= LIGNES - 4 and c <= COLS - 4:
                    if all(g[r+i][c+i] == p for i in range(4)):
                        return p

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

        if len(self.actions()) == 0:
            return 0

        return None

    def Terminal_test(self):

        return self.Utility(IA) is not None   

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
    root_game = Game(
        copy.deepcopy(state),
        IA
    )
    tree = MinMaxTree(
        rootp=IA,
        state="max",
        game=root_game
    )
    tree.generate_successors(depth=4)
    return tree.minimax_decision()

def Terminal_test(state):
    game = Game(state)
    return game.Terminal_test()

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
        print_board(game.grid)
        current_player = 1 if current_player == -1 else -1

        


if __name__ == "__main__":
    main()
       
