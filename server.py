import asyncio
import websockets
import uuid
import random
import traceback
event = asyncio.Event()
connected_clients = []
all_games = {}
class Game():
    def __init__(self):
        self.board = [[['e'] * 20]* 20]
    




class Player():
    
    def __init__(self, player_id,player_name,player_connection):
        self.player_id = player_id
        self.player_name = player_name
        self.player_connection = player_connection

def generate_game(player_id,connection):
    my_game_id = generate_id()
    all_games[my_game_id] = {}
    all_games[my_game_id][player_id] = connection
    return my_game_id

def generate_id():
    return random.randint(0,2147483647)

def send_to_id(client_id,msg):
    connected_clients[client_id].send(msg)

def change_to_readable_format(msg):
    return_list = []
    append_str = ""
    for letter in msg:
        if letter == "|":
            return_list.append(append_str)
            append_str = ""
            continue
        append_str += letter
    return_list.append(append_str)
    return return_list

def get_into_queue(player_id,connection):
    if len(all_games) != 0:
        for game_id, info_dict in all_games.items():
            if len(info_dict) == 1:
                all_games[game_id][player_id]=connection
                all_games[game_id]["world"] = [['e'] * 20 for _ in range(20)]
                all_games[game_id]["turn"] = -1
                playing_game = "first_connection"
                return (playing_game,game_id)
        game_id = generate_game(player_id,connection)
        playing_game = "waiting_connection"
    else:
        game_id = generate_game(player_id,connection)
        playing_game = "waiting_connection"
    return (playing_game,game_id)

async def recieve_message(connection):
    message = await connection.recv()
    readable_message = change_to_readable_format(message)
    return readable_message

# all_games{game_id:{player_id:connection|||player_id:connection}|||}

def check_win(game_id, x, y, player_type):
    board = all_games[game_id]["world"]

    directions = [
        (1, 0),   # horizontal
        (0, 1),   # vertical
        (1, 1),   # diagonal \
        (1, -1),  # diagonal /
    ]

    for dx, dy in directions:
        count = 1

        for direction in (1, -1):
            next_x = x + dx * direction
            next_y = y + dy * direction

            while (
                0 <= next_y < len(board)
                and 0 <= next_x < len(board[0])
                and board[next_y][next_x] == player_type
            ):
                count += 1
                next_x += dx * direction
                next_y += dy * direction

        if count >= 5:
            return True

    return False

async def handler(connection):
    my_id = generate_id()
    my_game_id = -1
    skip_first_lines = False
    name = ""
    oppenent_name = ""
    playing_game = "False"
    player_turn = -1
    oppenent_id = -1
    try:
        readable_message = await recieve_message(connection) 
        
        # player enters queue to join a game, either returns if they are p1 or p2
        if readable_message[0] == "enter_queue":
            playing_game,game_id = get_into_queue(my_id,connection)
            name = readable_message[1]
        # message when p1 connects and waits for p2 to send a message
        if playing_game == "waiting_connection":
            player_turn = 1
            readable_message = await recieve_message(connection)

        # message when p2 connects to a game using enter_queue, and get the oppenent_id, then sends its own id to p1
        if playing_game == "first_connection":
            player_turn = 2
            for other_id, other_connection in all_games[game_id].items():
                oppenent_id = other_id
                break

            await all_games[game_id][oppenent_id].send(f"relay|give_oppenent_info|{my_id}")
            readable_message = await recieve_message(connection)
        # p1 recieves the oppenent id, and then decides who goes first by sending a message back

        if readable_message[0] == "give_oppenent_info":
            oppenent_id = int(readable_message[1])
            if random.randint(1,2) == 1:
                await all_games[game_id][oppenent_id].send(f"relay|P1_goes_first")
                all_games[game_id]["turn"]=1
            else:
                await all_games[game_id][oppenent_id].send(f"relay|P2_goes_first")
                all_games[game_id]["turn"]=2
                skip_first_lines = True
                readable_message = await recieve_message(connection)


        if readable_message[0] == "P2_goes_first":
            skip_first_lines = True
            await connection.send("make_first_move")
            readable_message = await recieve_message(connection)

        if readable_message[0] == "P1_goes_first":
            await all_games[game_id][oppenent_id].send(f"make_first_move")
            skip_first_lines = False



        
        while True:
            if skip_first_lines == False:
                readable_message = await recieve_message(connection)
            if player_turn != all_games[game_id]["turn"]:
                continue
            skip_first_lines = False
            x = int(readable_message[1])
            y = int(readable_message[2])
            new_world = all_games[game_id]["world"]
            new_world[y][x] = player_turn
            all_games[game_id]["world"]=new_world
            if check_win(game_id,x,y,player_turn):
                await connection.send("you won :)")
                await all_games[game_id][oppenent_id].send(f"you lost :<")
            if all_games[game_id]["turn"] == 1:
                all_games[game_id]["turn"] = 2
            else:
                all_games[game_id]["turn"] = 1
            await connection.send(f"update{new_world}")
            await all_games[game_id][oppenent_id].send(f"move_update_relay|{new_world}")
            
    except (ConnectionResetError, BrokenPipeError, OSError) as error:
        print("connection lost")
    
    except Exception:
        traceback.print_exc()

    finally:
        print("smt happened idk what")

    

async def main():
    async with websockets.serve(handler, "", 8000):
        print("Server running at ws://localhost:8000")
        await asyncio.Future()  # runs forever
        # await asyncio.sleep(30)

asyncio.run(main())