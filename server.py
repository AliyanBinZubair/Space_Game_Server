import websockets
import asyncio
import json

client_id = 0
connected_clients = {} 
async def client_handler(client):
    global client_id, current_time, start_time, enemy_spawn_time, last_enemy_spawn
    current_id = client_id
    connected_clients[current_id] = client
    client_id +=1
    await client.send(json.dumps({"type":"id", "id": current_id}))
    print("client is connected!")
    try: 
        async for data in client:
            data = json.loads(data)
            for c_id, clients in connected_clients.items():
                if c_id != current_id:
                    await clients.send(json.dumps(data))
                else: 
                    pass
        
    except websockets.ConnectionClosed:
        print("connection closed!")
        connected_clients[current_id] = None
        client_id -=1
    except Exception as e:
        print(f"server:{e}")
    finally:
        connected_clients.pop(current_id)
        
async def main():
    async with websockets.serve(client_handler,"0.0.0.0",5555):
        print("server is started!")
        print("Waiting for client to connect")
        await asyncio.Future()
        
if __name__ == "__main__":
    asyncio.run(main())