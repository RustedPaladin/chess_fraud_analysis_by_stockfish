import pandas as pd
import numpy as np
import json as json
import pyarrow.parquet as pq
import game_classes
from matplotlib import pyplot
from stockfish import Stockfish

data = pq.read_table('./!data_skoltech/online/games_moves/chess_sample_1/part-00000.parquet')
# data = pq.read_table('./DATA_LOCAL/games_with_moves.parquet')


def load_to_obj(data, lan_list, games_list):
    i = 1
    for g in range(1000): #len(data[0])
        if len(data['WhiteElo'][g].as_py()) > 0 and len(data['BlackElo'][g].as_py()) > 0:
            game_data = {
            'white_player': data['White'][g],
            'white_elo': data['WhiteElo'][g],
            'black_player': data['BlackElo'][g],
            'black_elo': data['BlackElo'][g],
            'length': data['Moves_length'][g].as_py(),
            'result': data['Result'][g],
            'moves_lan': lan_list[g]
            }
            this_game = game_classes.Game(game_data)
            games_list.append(this_game)
            i += 1
            # print(i, 'appended')
    return(games_list)

def read_lan_games_csv(path):
    csv = pd.read_csv(path)
    games_list = []
    for i in range(len(csv.iloc[:, 1])):
        games_list.append(json.loads(csv.iloc[i, 1]))
    return games_list


#START


#LOAD GAMES
path = './DATA_LOCAL/1000_games_lan.csv'
clean_lan_list = read_lan_games_csv(path)
games_list = []

games_list = load_to_obj(data, clean_lan_list, games_list)

#INIT STOCKFISH
stockfish_parameters = {
            "Debug Log File": "",
            "Contempt": 0, #???
            "Min Split Depth": 0, #???
            "Threads": 2, # should be kept at less than the number of logical processors on your computer.
            "Ponder": False, #???
            "Hash": 16, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
            "MultiPV": 1, #???
            "Skill Level": 20, #???
            "Move Overhead": 10, #???
            "Minimum Thinking Time": 0, #is needed?
            # "Slow Mover": 100,
            "UCI_Chess960": False,
            "UCI_LimitStrength": False,
            "UCI_Elo": 1000 #try_change
        }
        
stf = Stockfish(path='./stockfish/stockfish-ubuntu-x86-64-sse41-popcnt', depth = 1)


# FIND GENIUS POSITIONS
start_fraction = 15 / 100
end_fraction = 85 / 100
for i, g in enumerate(games_list):
    g.set_main_stf(stf)
    g.find_genius_moves_stf(g.pos_eval_by_stf_all_moves, start_fraction, end_fraction)
    print(i, len(g.genius_moves))

#FIND POSITION MATCHING

        

# def gain_occurs_elo_range(games_list, min_elo, max_elo):
#     gains_list = []
#     occur_list = []
#     for g in games_list:
#         for m in g.list_of_moves:
#             if m.gain != None : #and (m.gain > 1000 or m.gain < -1000)
#                 if m.player_elo >= min_elo and m.player_elo <= max_elo:
#                     if m.gain not in gains_list:
#                         gains_list.append(m.gain)
#                         occur_list.append(1)
#                     else:
#                         occur_list[gains_list.index(m.gain)] +=1
#     tuples_list = []
#     for i in range(len(gains_list)):
#         tuples_list.append((gains_list[i], occur_list[i]))
#     tuples_list.sort(key = lambda tuple : tuple[1])
#     return tuples_list



# moves_by_elo = gain_occurs_elo_range(games_list, 2000, 3000)
# print(moves_by_elo)

# x = []
# y = []
# for m in moves_by_elo:
#     x.append(m[0])
#     y.append(m[1])
# pyplot.scatter(x, y)
# pyplot.show()



