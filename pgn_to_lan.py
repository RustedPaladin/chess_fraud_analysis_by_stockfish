import pyarrow.parquet as pq
import chess.pgn
import chess
import io
import pandas as pd
import json

data = pq.read_table('./!data_skoltech/online/games_moves/chess_sample_1/part-00000.parquet')

def get_moves_from_pgn(pgn_obj):
    pgn = io.StringIO(pgn_obj.as_py())
    game = chess.pgn.read_game(pgn)
    string_moves_list = []    
    for m in game.mainline_moves():
        string_moves_list.append(m.__str__())
    return(string_moves_list)

games_list = []
# for i in data['Moves'][0:1000]:
#     lan_list = get_moves_from_pgn(i)
#     games_list.append(json.dumps(lan_list))
# print(len(games_list))
# df = pd.DataFrame(games_list, columns=['lan_list'])

# print(df)
# df.to_csv('./DATA_LOCAL/1000_games_lan.csv')

def read_lan_games_csv(path):
    csv = pd.read_csv(path)
    games_list = []
    for i in range(len(csv.iloc[:, 1])):
        games_list.append(json.loads(csv.iloc[i, 1]))
    return games_list


path = './DATA_LOCAL/1000_games_lan.csv'

clean_games_list = read_lan_games_csv(path)
print(len(clean_games_list))

# csv = pd.read_csv('./DATA_LOCAL/test.csv')
# print(csv.iloc[1, 1])