# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 10:11:07 2026

@author: leste
"""
import random

# puissance 4
def print(mat):
    return print("Affichage de la matrice") 

def IA_Decision(mat):
    return random.randint(0, 11)

def Terminal_Test(mat):
    return False

class Game:
    def __init__(self, start=1):
        self.player1 = start
        self.player2 = 1 if start == 1 else -1
        self.state = [[0 for _ in range(12)] for _ in range(6)]
        self.winner = None

    def play(self, player, col):
        assert col >= 0 and col < 12, "Erreur"
        row = 0
        while self.state[row][col] == 0:
            row += 1
        
        row = row - 1
        self.state[row][col] = player
    
    def __str__(self):
        return ""

        


def main():
    start = int(input("Qui commence ? [1=IA, -1=Humain]: "))
    game = Game(start)
    current_player = 1 if start == 1 else -1

    while True:
        if current_player == 1:
            col = IA_Decision()
        else:
            col = input("Entrez une colonne [0-11]: ")
        game.play(current_player, col)
        

    

if __name__ == "__main__":
    main()