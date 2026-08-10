import asyncio
import websockets
import uuid

all_games = []
connected_clients = []

class Game():
    pass




class Player():
    
    def __init__(self, player_id,player_name,player_connection):
        self.player_id = player_id
        self.player_name = player_name
        self.player_connection = player_connection



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



async def handler(connection):
    my_id =  random.randint(0,2147483647)
    connected_clients[my_id]=connection
    type_player = -1
    game_playing = False
    own_queded_message = False
    in_queue = False
    try:
        while True:
            message = await connection.recv()
            readable_message = change_to_readable_format(message)
            if readable_message[0] == "start_client":
                player = Player(my_id,readable_message[1],connection)
                connected_clients.append(player)
            connection.send()
                    
                
                
            
            
            
    except:
        pass


    # finnaly:
    #     pass

    

async def main():
    async with websockets.serve(handler, "", 8000):
        print("Server running at ws://localhost:8000")
        await asyncio.Future()  # runs forever
        # await asyncio.sleep(30)

asyncio.run(main())