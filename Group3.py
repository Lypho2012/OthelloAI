#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
An AI player for Othello. This is the template file that you need to  
complete.

@author: David Chung dic211, Batu Yalçın by2330
"""

import random
import sys
import time
import heapq as hq
init = 0
moveCount = 0
depth = 4
class MaxHeap:
    def __init__(self):
        self.data = []

    def top(self):
      if not self.data:
        return False
      return True

    def push(self, val):
        hq.heappush(self.data, [-val[0],val[1],val[2]])

    def pop(self):
        popped = hq.heappop(self.data)
        return [popped[1],popped[2]]



# You can use the functions in othello_shared to write your AI 
from othello_shared import find_lines, get_possible_moves, get_score, play_move

weightTable  = [[4,-3,2,2,2,2,-3,4],   #something was weird with the previous weight table so I just put in the one I had from YOURGROUP_ai.py
                [-3,-4,-1,-1,-1,-1,-4,-3],
                [2,-1,1,0,0,1,-1,2],
                [2,-1,0,1,1,0,-1,2],
                [2,-1,0,1,1,0,-1,2],
                [2,-1,1,0,0,1,-1,2],
                [-3,-4,-1,-1,-1,-1,-4,-3],
                [4,-3,2,2,2,2,-3,4]]


def compute_utility(board, color): # color = 1 = black color = 2 = white
    opp_color = 1 if color == 2 else 2
    colorTuple = get_score(board)
    score = colorTuple[color-1]-colorTuple[opp_color-1]
    colorWList = [0,0,0]
    colorWList[color] = 1
    colorWList[opp_color] = -1
    column = len(board)
    for i in range(column):
      for j in range(column):
        if board[i][j] != 0:
          score += weightTable[i][j]*colorWList[board[i][j]]

    return score
        
############ MINIMAX ###############################

def minimax_min_node(board, color):
    opp_color = 1 if color == 2 else 2
    player = color
    if len(get_possible_moves(board,player)) == 0:
      return compute_utility(board,color)
    moves = get_possible_moves(board,player)
    mini = float("inf")
    for (i,j) in moves: #i,j are coor
      new_board = play_move(board,color,i,j)
      coorBoard = ((i,j),minimax_max_node(new_board, opp_color))
      #print(coorBoard[1])
      try:
        if mini > coorBoard[1][0]:
          mini = coorBoard[1][0]
      except TypeError:
        if mini > coorBoard[1]:
          mini = coorBoard[1]

    return mini

    
def minimax_max_node(board, color):
    opp_color = 1 if color == 2 else 2
    player = color
    if len(get_possible_moves(board,player)) == 0:
      return compute_utility(board,color)
    moves = get_possible_moves(board,player)
    maxi = float("-inf") 
    for (i,j) in moves: #i,j are coor
      new_board = play_move(board,color,i,j)
      coorBoard = ((i,j),minimax_min_node(new_board, opp_color))
      if maxi < coorBoard[1]:
        maxi = coorBoard[1]
        coords = (i,j)

    return maxi,coords

    
def select_move_minimax(board, color):
    move = minimax_max_node(board,color)
    #print(move[1])
    print("Playing",move[1][0],",",move[1][1], file = sys.stderr)
    return move[1] 

############ ALPHA-BETA PRUNING #####################

def alphabeta_min_node(board, color, alpha, beta, level, d):#level is the current level, d is the depth limit

    opp_color = 1 if (color == 2) else 2 #get opponent's color
    possible_moves = get_possible_moves(board, color) # get list of possible moves
    if len(possible_moves) == 0:#no possible moves
      return compute_utility(board, color)#return utility value
    if level > d:
      return compute_utility(board,color) 
    
    heap = []

    for (x,y) in possible_moves:
      newBoard = play_move(board,color,x,y)
      hq.heappush(heap, [compute_utility(newBoard,color),newBoard]) #add to heap


    while heap:#i,j are coords
      new_board = hq.heappop(heap)[1]
      max_move = alphabeta_max_node(new_board,opp_color,alpha,beta,level+1,d)[0]
      if max_move == "random":
        return [max_move]
        break
      if max_move < beta:
        beta = max_move
      if alpha >= beta:
        break

    return beta

def alphabeta_max_node(board, color, alpha, beta, level, d):
    opp_color = 1 if (color == 2) else 2 #get opponent's color
    possible_moves = get_possible_moves(board, color) # get list of possible moves
    if len(possible_moves) == 0:#no possible moves
      return (compute_utility(board, color),None)#return utility value 
    if level > d:
      return (compute_utility(board,color),None)

    maxheap = MaxHeap()

    for (x,y) in possible_moves:
      newBoard = play_move(board,color,x,y)
      maxheap.push([compute_utility(newBoard,color),(x,y),newBoard]) #add to heap


    while maxheap.top():#i,j are coords
      if time.perf_counter()-init>=18:
        print(time.perf_counter()-init, file = sys.stderr)
        return ["random","random"]
      popped = maxheap.pop()
      new_board = popped[1]
      min_move = alphabeta_min_node(new_board,opp_color,alpha,beta,level+1,d)
      if min_move == ["random"]:
        return min_move
      if min_move > alpha:
        alpha = min_move
        coords = popped[0]
      if alpha >= beta:
        break
    try:
      return alpha, coords
    except UnboundLocalError:
      return float("-inf"),None

def select_move_alphabeta(board, color): 
    #print("Selecting move\n",file = sys.stderr)
    global init
    global moveCount
    global depth
    moveCount+=1
    if moveCount == 27:
      print("MiniMax Takes Over", file = sys.stderr)
    if moveCount >= 27:
      select_move_minimax(board, color)
      return select_move_minimax(board,color)
    else:  
      move = alphabeta_max_node(board,color, float('-inf'), float('inf'),1,4)
      if move[0]=="random":
        init = time.perf_counter()
        move = alphabeta_max_node(board,color, float('-inf'), float('inf'),1,4)
      print(move[1],file = sys.stderr)
      return move[1]
      #print("\nSelected move\n" + str(time.perf_counter()-inti),file = sys.stderr)


####################################################
def run_ai():
    global init
    """
    This function establishes communication with the game manager. 
    It first introduces itself and receives its color. 
    Then it repeatedly receives the current score and current board state
    until the game is over. 
    """
    #print("Minimax AI") # First line is the name of this AI  
    print("Alpha-Beta ")
    color = int(input()) # Then we read the color: 1 for dark (goes first), 
                         # 2 for light. 
    
    while True: # This is the main loop 
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input() 
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over. 
            print 
        else: 
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The 
                                  # squares in each row are represented by 
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)
                    
            # Select the move and send it to the manager 
            #movei, movej = select_move_minimax(board, color)
            init = time.perf_counter()
            movei, movej = select_move_alphabeta(board, color)
            print("{} {}".format(movei, movej)) 


if __name__ == "__main__":
    run_ai()
