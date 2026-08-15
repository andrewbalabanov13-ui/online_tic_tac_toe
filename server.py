import asyncio
import websockets
import uuid
import random

new_positions = ()
event = asyncio.Event()
connected_clients = []
player_turn = -1
world = [['e'] * 20]* 20
class Game():
    def __init__(self):
        self.board = [['e'] * 10]* 10
    




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

def check_if_player_won(player_type):
    for row in range(len(world)):
        for col in range(len(row)):
            try:
                if (world[row][col] == player_type and
                    world[row][col + 1] == player_type and
                    world[row][col + 2] == player_type and
                    world[row][col + 3] == player_type and
                    world[row][col + 4] == player_type
                ):
                    return True
            
            except:
                pass
                
            try:
                if (world[row][col] == player_type and
                    world[row + 1][col] == player_type and
                    world[row + 2][col] == player_type and
                    world[row + 3][col] == player_type and
                    world[row + 4][col] == player_type
                ):
                    return True      

            except:
                pass
            
            try:
                if (world[row][col] == player_type and
                    world[row + 1][col + 1] == player_type and
                    world[row + 2][col + 2] == player_type and
                    world[row + 3][col + 3] == player_type and
                    world[row + 4][col + 4] == player_type
            ):
                    return True
            
            except: 
                pass

            try:
                if (world[row][col] == player_type and
                    world[row - 1][col + 1] == player_type and
                    world[row - 2][col + 2] == player_type and
                    world[row - 3][col + 3] == player_type and
                    world[row - 4][col + 4] == player_type
                ):
                    return True
            
            except:
                pass
    return False

async def handler(connection):
    global player_turn
    
    my_id =  random.randint(0,2147483647)
    game_playing = False
    skip_first_lines = False
    player_type = 0
    try:
        message = await connection.recv()
        readable_message = change_to_readable_format(message)   
        if readable_message[0] == "start_client":
            player = Player(my_id,readable_message[1],connection)
            connected_clients.append(player)
            print("player_connected_into_queue")

        if len(connected_clients) == 1:
            await event.wait()
        elif len(connected_clients) == 2:
            player_type = 1
            event.set()
            await connected_clients[player_type].player_connection.send(f"opponent|{connected_clients[player_type - 1].player_name}")
            await connected_clients[player_type - 1].player_connection.send(f"opponent|{connected_clients[player_type].player_name}")

        if player_type == 0:
            await event.wait()
        
        if player_type == 1:
            if random.randint(1,2) == 1:
                player_turn = 0
                skip_first_lines = True
            else:
                player_turn = 1
                await connected_clients[player_type - 1].player_connection.send(f"relay|start_game")
            event.set()
        
        if readable_message[0] == "start_game":
            player_turn = 1
            skip_first_lines = True

        while True:
            if skip_first_lines == False:
                await event.wait()

            skip_first_lines = False

            if player_turn == player_type:
                message_turn = await connection.recv()
                readable_message_turn = change_to_readable_format(message_turn)
                x = int(readable_message_turn[1])
                y = int(readable_message_turn[2])

                if x < 0 or x > 20 or y < 0 or y > 20:
                    await connection.send("resend_message")
                    
                if world[y][x] != 'e':
                    skip_first_lines = True
                    await connection.send("resend_message")
                    continue
                
                world[y][x] = str(player_turn)

                if check_if_player_won(player_type):
                    await connected_clients[player_type].player_connection.send(f"player_won|{player_type}")
                    await connected_clients[player_type - 1].player_connection.send(f"player_won|{player_type}")   

                await connected_clients[player_type].player_connection.send(f"update|{x}|{y}|{player_turn}")
                await connected_clients[player_type - 1].player_connection.send(f"update|{x}|{y}|{player_turn}")

                if player_turn == 0:
                    player_turn = 1
                else:
                    player_turn = 0

                event.set()



                                     
                
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