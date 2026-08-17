import asyncio
import websockets
import uuid
import random

event = asyncio.Event()
connected_clients = []
all_games = {}
player_turn = -1
world = [[['e'] * 20] * 20]
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
    all_games[my_game_id][my_id] = connection

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

def get_into_queue(player_id):
    if len(all_games) != 0:
        for game_id, info_dict in all_games.items():
            if len(info_dict) == 1:
                all_games[game_id][player_id]=connection
                playing_game = "first_connection"
                return (playing_game,game_id)
        generate_game(player_id,connection)
        playing_game = "waiting_connection"
    else:
        generate_game(player_id,connection)
        playing_game = "waiting_connection"
    return (playing_game,game_id)

def recieve_message(connection):
    message = await connection.recv()
    readable_message = change_to_readable_format(message)
    return readable_message

# all_games{game_id:{player_id:connection|||player_id:connection}|||}

async def handler(connection):
    global player_turn
    my_id = generate_id()
    my_game_id = -1
    playing_game = "False"
    oppenent_id = -1
    try:
        recieve_message = recieve_message(connection) 
        
        if readable_message[0] == "start_client":
            player = Player(my_id,readable_message[1],connection)
            connected_clients.append(player)
        
        # player enters queue to join a game, either returns if they are p1 or p2
        if readable_message[0] == "enter_queue":
            playing_game,game_id = get_into_queue(my_id)

        # message when p1 connects and waits for p2 to send a message
        if playing_game == "waiting_connection":
            await connection.send("")
            readable_message = recieve_message(connection)

        # message when p2 connects to a game using enter_queue, and get the oppenent_id, then sends its own id to p1
        if playing_game == "first_connection":
            for other_id, other_connection in all_games[game_id].items():
                oppenent_id = other_id
                break

            await all_games[game_id][oppenent_id].send(f"relay|give_oppenent_id|{my_game_id}")

        # p1 recieves the oppenent id, and then decides who goes first by sending a message back
        if readable_message[0] == "give_oppenent_id":
            oppenent_id = readable_message[1]
            if random.randint(1,2) == 1:
                all_games[game_id][oppenent_id].send(f"relay|P1_goes_first")
            else:
                all_games[game_id][oppenent_id].send(f"relay|P2_goes_first")
            readable_message = recieve_message(connection)

                

    except (ConnectionResetError, BrokenPipeError, OSError) as error:
        print("connection lost")
    
    except Exception as error:
        print(f"connection lost, reason: {error}")

    finally:
        print("smt happened idk what")

    

async def main():
    async with websockets.serve(handler, "", 8000):
        print("Server running at ws://localhost:8000")
        await asyncio.Future()  # runs forever
        # await asyncio.sleep(30)

asyncio.run(main())