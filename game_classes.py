import pandas as pd
import numpy as np
import json as json
import pyarrow.parquet as pq
from stockfish import Stockfish
import chess
import chess.pgn
import io

def clear_string(string):
    new_string = str('')
    take = True
    for s in string:
        if s == '{':
            take = False
        if s == '}':
            take = True
        if take == True:
            new_string += s
    new_string = new_string.replace('}', '')
    return new_string

class Game():
    def __init__(self, game_data):
        #PLAYERS DATA
        self.white_player = game_data['white_player']
        self.white_elo = game_data['white_elo']
        self.black_elo = game_data['black_elo']
        self.black_player = game_data['black_player']
        
        #GAME DATA
        self.result = game_data['result']
        self.length = game_data['length']
        self.moves_lan = game_data['moves_lan']

        #MOVES LISTS
        self.all_moves = []
        self.white_moves = []
        self.black_moves = []
        self.genius_moves = []

        #GAME SPLITS
        self.starting_fraction = 15/100
        self.finishing_fraction = 85/100
        self.opening_white = []
        self.middle_white = []
        self.ending_white = []
        self.opening_black = []
        self.middle_black = []
        self.ending_black = []
        
        #LOAD GAME MOVES
        # print('self.moves_pgn', type(self.moves_pgn))
        # moves_list = self.get_moves_from_pgn(self.moves_pgn)
        for i, m in enumerate(self.moves_lan):
            new_move = Move(number=i, move = m, white_elo = self.white_elo, black_elo = self.black_elo) #convert pyarrow values to python
            self.all_moves.append(new_move)
        
        #GAME SPLIT
        # self.split_game(self.starting_fraction, self.finishing_fraction)
        # self.split_color()

        #INIT STOCKFISH

        #FIND GENIUS MOVES
        start_index = int(len(self.all_moves) * self.starting_fraction)
        # print('start_index', start_index)
        end_index = int(len(self.all_moves) * self.finishing_fraction)
        # print('end_index', end_index)
        # self.find_genius_moves_stf(self.pos_eval_by_stf, start_index, end_index)
    
    def get_moves_from_pgn(self, pgn):
        pgn = io.StringIO(clear_string(pgn))
        # game = chess.pgn.read_game(pgn)
        # string_moves_list = []
        # for m in game.mainline_moves():
        #     string_moves_list.append(m.__str__())
        # return(string_moves_list)

    def split_color(self):
        for m in self.all_moves:
            if m.number % 2 == 0:
                self.white_moves.append(m)
            else:
                self.black_moves.append(m)


    def split_game(self, starting_fraction, finishing_fraction):
        self.length = self.all_moves[-1].number
        for m in self.all_moves:
            if m.number <= int(self.length / starting_fraction):
                if m.color == 'White':
                    self.opening_white.append(m)
                else:
                    self.opening_black.append(m)
            if m.number > int(self.length / starting_fraction) and m.number <= int(self.length / finishing_fraction):
                if m.color == 'White':
                    self.middle_white.append(m)
                else:
                    self.middle_black.append(m)
            if m.number > int(self.length / finishing_fraction):
                if m.color == 'White':
                    self.ending_white.append(m)
                else:
                    self.ending_black.append(m)
    
    def  find_genius_moves_stf(self, pos_eval_func, start_fraction, end_fraction):
        for r in range(int(self.length * start_fraction), int(self.length * end_fraction)): #end != last move
            #init analysis
            current_moves = []
            next_move = self.all_moves[r+1]
            for l in range(0, r):
                # print('l', l)
                current_moves.append(self.all_moves[l].move)
                # print('self.list_of_moves[l].move', self.all_moves[l].move)
                # print('self.list_of_moves[l].color', self.all_moves[l].color)
            # print('current_moves', current_moves)
            
            #eval_position
            pos_eval = pos_eval_func(current_moves)
            
            #check_next_move
            if pos_eval[0] == True:
                # print('pos_eval[2]', pos_eval[2], 'next_move', next_move.move)
                if pos_eval[2] == next_move.move:
                    next_move.is_genius = True
                    self.genius_moves.append(next_move)

    def set_main_stf(self, stf):
        self.main_stf = stf
    
    def pos_eval_by_stf_factor(self, current_moves):
        #init
        # print('EVAL_START')
        self.main_stf.set_position(current_moves)
        current_eval = self.main_stf.get_evaluation()['value']
        if current_eval == 0:
            current_eval += 1
        # print('current_eval', current_eval)
        n_moves = 2
        delta_coeff = 2
        best_moves = self.main_stf.get_top_moves(n_moves)
        
        #check if pos critical
        is_critical = False
        g_coeff = 0
        # for i in range(n_moves-1):
        if best_moves[0]['Centipawn'] - current_eval >= delta_coeff * (best_moves[1]['Centipawn'] - current_eval):
            # print('best_moves[i][Centipawn]', best_moves[i]['Centipawn'] - current_eval)
            # print('best_moves[i][Centipawn]', best_moves[i]['Centipawn'])
            # print('best_moves[i+1][Centipawn]', best_moves[i+1]['Centipawn'] - current_eval)
            is_critical = True
            try:
                g_coeff = best_moves[0]['Centipawn'] / best_moves[1]['Centipawn']
            except:
                g_coeff = best_moves[0]['Centipawn'] / ( best_moves[1]['Centipawn'] + 1 )
            g_coeff = abs(g_coeff)
            # print('g_coeff', g_coeff)
            best_move = best_moves[0]['Move']
            # cur_g_coeff = best_moves[i]['Centipawn'] / best_moves[i+1]['Centipawn']
            # if cur_g_coeff > g_coeff:
            #     g_coeff = cur_g_coeff
            #     best_move = 

    def pos_eval_by_stf_fixed(self, current_moves):
        #init
        # print('EVAL_START')
        self.main_stf.set_position(current_moves)
        current_eval = self.main_stf.get_evaluation()['value']
        # print('current_eval', current_eval)
        n_moves = 1
        delta_coeff = 2
        best_moves = self.main_stf.get_top_moves(n_moves)
        
        #check if pos critical
        is_critical = False
        g_coeff = 0
        # for i in range(n_moves-1):
        if abs(best_moves[0]['Centipawn'] - current_eval) > 15:
            # print('best_moves[i][Centipawn]', best_moves[i]['Centipawn'] - current_eval)
            # print('best_moves[i][Centipawn]', best_moves[i]['Centipawn'])
            # print('best_moves[i+1][Centipawn]', best_moves[i+1]['Centipawn'] - current_eval)
            is_critical = True
            # print('g_coeff', g_coeff)
            best_move = best_moves[0]['Move']
            # cur_g_coeff = best_moves[i]['Centipawn'] / best_moves[i+1]['Centipawn']
            # if cur_g_coeff > g_coeff:
            #     g_coeff = cur_g_coeff
            #     best_move = 

    def pos_eval_by_stf_all_moves(self, current_moves):
        #init
        # print('EVAL_START')
        self.main_stf.set_position(current_moves)
        # print('current_eval', current_eval)
        best_move = self.main_stf.get_best_move()
        
        #check if pos critical
        g_coeff = 0
        # for i in range(n_moves-1):
    
        # print('best_moves[i][Centipawn]', best_moves[i]['Centipawn'] - current_eval)
        # print('best_moves[i][Centipawn]', best_moves[i]['Centipawn'])
        # print('best_moves[i+1][Centipawn]', best_moves[i+1]['Centipawn'] - current_eval)
        is_critical = True
        # print('g_coeff', g_coeff)
        # cur_g_coeff = best_moves[i]['Centipawn'] / best_moves[i+1]['Centipawn']
            # if cur_g_coeff > g_coeff:
            #     g_coeff = cur_g_coeff
            #     best_move = 
                
        #return result
        if is_critical == True:
            return([is_critical, g_coeff, best_move])
        else:
            return([is_critical])
    
    # def evaluate_moves_weak_strong(weak_stf, strong_stf):





class Move():
    def __init__(self, number, move, white_elo, black_elo):
        self.number = number
        self.move = move
        self.is_genius = False
        self.g_coeff = 0
        self.weak_estimate = 0
        self.strong_estimate = 0
        if self.number % 2 == 0:    
            self.color = 'White'
        else:
            self.color = 'Black'
            self.player_elo = int(black_elo.as_py())
        # if position != None and prev_position != None:
        #     self.gain = position - prev_position
        # else:
        #     self.gain = None
        # self.abs_position = position
        # if self.color == 'Black':
        #     self.relat_position = abs(position)
        # else:
        #     self.relat_position = self.abs_position