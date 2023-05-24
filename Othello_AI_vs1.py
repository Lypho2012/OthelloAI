#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
An AI player for Othello. Uses different weights at each stage of game.

@author: YOUR NAME AND UNI 
"""

import random
import sys
import time
from threading import Timer
from othello_game import AiPlayerInterface
# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def compute_utility(board, color):  # heuristic
    darkscore, lightscore = get_score(board)
    if color == 1:
        return darkscore - lightscore
    else:
        return lightscore - darkscore


weight_file = open("weight.txt","r+")
weights_from_file = weight_file.readlines()
weights_list = []
for dynamic_weight in weights_from_file:
    weights_list.append(list(map(float, dynamic_weight.strip().split(" "))))
weight_file.close()
def heuristic(board,color):
    #global weights  
    #weights = [1,1,1,1,1,1]
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    if AiPlayerInterface.moves_made <= 5:
        weights = weights_list[0]
    elif AiPlayerInterface.moves_made <= 10:
        weights = weights_list[1]
    elif AiPlayerInterface.moves_made <= 15:
        weights = weights_list[2]

    '''
    utility = total util
    corners = # of corners
        = 100*(max player corners heuristic-min player corners heuristic)/(max player corners heuristic+min player corners heuristic)
    %piecesonwall = 
    actual + potential mobility(# of opposing disks next to opposing state) = 
    stability (can be captured within 1 move, 1+ moves, or never) 
        = 100*(max player stability value - min player stability value)/ (max player stability value + min player stability value)
    
    early game: focus on stability and mobility
    middle: corners and stability
    later: mostly on utility (when search doesn't exceed depth limit)
    '''
    utility = 0
    corners = 0
    piecesOnWall = 0
    mobility = 0
    potential_mobility = 0
    stability = 0
    p1_count = 0
    p2_count = 0
    for i in range(len(board)):
        for j in range(len(board)):
            # mobility
            if board[i][j] == 0:
                lines = find_lines(board, i, j, color)
                mobility += len(lines)
                opp_lines = find_lines(board, i, j, opp_color)
                stability += len(opp_lines)

            if i != 0 and board[i - 1][j] == opp_color:
                potential_mobility += 1
            if i != len(board) - 1 and board[i + 1][j] == opp_color:
                potential_mobility += 1
            if j != 0 and board[i][j - 1] == opp_color:
                potential_mobility += 1
            if j != len(board) - 1 and board[i][j + 1] == opp_color:
                potential_mobility += 1

            # utility
            if board[i][j] == 1:
                p1_count += 1
            elif board[i][j] == 2:
                p2_count += 1
            # corners
            if i == 0 or i == len(board) - 1:
                if (j == 0 or j == len(board) - 1) and board[i][j] == color:
                    corners += 1
            # piecesOnWall
            if (i == 0 or i == len(board) - 1 or j == 0
                    or j == len(board) - 1) and board[i][j] == color:
                piecesOnWall += 1

    if color == 1:
        utility = p1_count - p2_count
    else:
        utility = p2_count - p1_count

    features = [
        utility, corners, piecesOnWall, mobility, potential_mobility, stability
    ]
    #weights = [wutility, wcorners, wpiecesOnWall, wmobility, wpotential_mobility, wstability]
    result = [0] * len(features)
    for i in range(len(features)):
        result[i] = features[i] * weights[i]
    #print(sum(result),file=sys.stderr)
    return sum(result), features



############ ALPHA-BETA PRUNING #####################

total_states = 0
#alphabeta_min_node(board, color, alpha, beta, level, limit)
def alphabeta_min_node(board, color, alpha):
    global timedOut
    if timedOut:
        return heuristic(board,color)

    #global total_states

    #if total_states >= 4000:
    #    return heuristic(board,color)
        #return compute_utility(board, color)

    #total_states += 1

    opp_color = 1 if color == 2 else 2
    moves = get_possible_moves(board, opp_color)
    minUtil = float("inf")  # local beta
    if moves == []:
        return compute_utility(board, color)

    successors = [
        play_move(board, opp_color, move[0], move[1]) for move in moves
    ]

    successors.sort(key=lambda state: compute_utility(state, color))
    features = []
    f = []
    for new_board in successors:
        #new_board = play_move(board,opp_color,move[0],move[1])
        temp = alphabeta_max_node(new_board, color, minUtil)
        if isinstance(temp,int):
            utility = temp
        else:
            utility,f = temp
        
        if utility < minUtil:
            minUtil = utility
            if f:
                features = f
        if minUtil < alpha:
            #print("prune min node", file=sys.stderr)
            break

    return minUtil, features


#alphabeta_max_node(board, color, alpha, beta, level, limit)
def alphabeta_max_node(board, color, beta):
    global timedOut
    if timedOut:
        return heuristic(board,color)

    #global total_states
    #if total_states >= 4000:
    #    return heuristic(board,color)
        #return compute_utility(board, color)
    #total_states += 1

    
    moves = get_possible_moves(board, color)
    maxUtil = -float('inf')  #local alpha
    if moves == []:
        return compute_utility(board, color)

    successors = [play_move(board, color, move[0], move[1]) for move in moves]

    successors.sort(key=lambda state: compute_utility(state, color),
                    reverse=True)
    features = []
    f = []
    for new_board in successors:
        #new_board = play_move(board,color,move[0],move[1])
        temp = alphabeta_min_node(new_board, color, maxUtil)
        if isinstance(temp,int):
            utility = temp
        else:
            utility,f = temp
        
        if utility > maxUtil:
            maxUtil = utility
            if f:
                features = f
        if maxUtil > beta:
            #print("prune max node", file=sys.stderr)
            break

    return maxUtil, features

timedOut = False

def timeOut():
    global timedOut
    timedOut = True

def select_move_alphabeta(board, color):
    global timedOut
    #global total_states
    #total_states += 1

    best_move = None
    alpha = -float('inf')
    #beta = float('inf')
    features = []
    f = []
    moves = get_possible_moves(board, color)
    t = 9/len(moves)
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        timer = Timer(t, lambda:timeOut())
        timer.start()
        temp = alphabeta_min_node(new_board, color, alpha)
        timedOut = False
        timer.cancel()
        if isinstance(temp,int):
            utility = temp
        else:
            utility,f = temp
        if utility > alpha:
            alpha = utility
            best_move = move
            if f:
                features = f
        #print("Total states expanded:", total_states, file=sys.stderr)
        #total_states = 0
    file = open("data.txt","a")
    
    if features != []:
        file.writelines(str(features)+"\n")
    file.close()
    #print("Total states expanded:", total_states, file=sys.stderr)
    #print(best_move,file=sys.stderr)
    return best_move[0], best_move[1]


####################################################
#final_board = None
def run_ai():
    """
    This function establishes communication with the game manager. 
    It first introduces itself and receives its color. 
    Then it repeatedly receives the current score and current board state
    until the game is over. 
    """
    #print("Heuristic AI")  # First line is the name of this AI
    color = int(input())  # Then we read the color: 1 for dark (goes first),
    # 2 for light.

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL":  # Game is over.
            print
        else:
            board = eval(
                input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            #movei, movej = select_move_minimax(board, color)
            movei, movej = select_move_alphabeta(board, color)
            print("{} {}".format(movei, movej))

            '''file = open("board.txt","w")
            file = file.truncate(0)
            file = open("board.txt","a")
            for line in board:
                line = list(map(str,line))
                file.writelines(" ".join(line)+"\n")
            file.close()'''

if __name__ == "__main__":
    run_ai()



############ MINIMAX ###############################


def minimax_min_node(board, color):
    global total_states
    total_states += 1
    opp_color = 1 if color == 2 else 2
    moves = get_possible_moves(board, opp_color)
    minUtil = float("inf")
    if moves == []:
        return compute_utility(board, color)

    for move in moves:
        new_board = play_move(board, opp_color, move[0], move[1])
        utility = minimax_max_node(new_board, color)
        if utility < minUtil:
            minUtil = utility

    return minUtil


def minimax_max_node(board, color):
    global total_states
    total_states += 1
    #opp_color = 1 if color == 2 else 2
    moves = get_possible_moves(board, color)
    maxUtil = -float('inf')
    if moves == []:
        return compute_utility(board, color)

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        utility = minimax_min_node(new_board, color)
        if utility > maxUtil:
            maxUtil = utility

    return maxUtil


def select_move_minimax(board, color):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  
    """
    global total_states
    total_states += 1

    #opp_color = 1 if color == 2 else 2
    best_move = None
    maxUtil = -float('inf')
    for move in get_possible_moves(board, color):
        new_board = play_move(board, color, move[0], move[1])
        utility = minimax_min_node(new_board, color)
        if utility > maxUtil:
            maxUtil = utility
            best_move = move

    print("Total states expanded:", total_states, file=sys.stderr)

    return best_move[0], best_move[1]
