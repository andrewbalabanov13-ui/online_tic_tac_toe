import asyncio
import websockets
import uuid

queded_connections = []
connected_clients = {}

async def handler(connection):
    my_id =  random.randint(0,2147483647)
    connected_clients[my_id]=connection
    in_queue = False
    try:
        while True:
            message = await connection.recv()
            if message == "queue":
                in_queue = True
            
            if in_queue and len(queded_connections) < 2:
                queded_connections.append(connection)
            
            await connection.send()
    
    except:
        pass


    

async def main():
    async with websockets.serve(handler, "", 8000):
        print("Server running at ws://localhost:8000")
        await asyncio.Future()  # runs forever
        # await asyncio.sleep(30)

asyncio.run(main())