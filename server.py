import websockets, asyncio, json, sqlite3, datetime, os


db = sqlite3.connect("scores.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        score INTEGER NOT NULL,
        date TEXT NOT NULL
    )
""")
db.commit()


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

            msg_type = data.get("type")

            if msg_type == "submit_score":
                db.execute(
                    "INSERT INTO scores (name, score, date) VALUES (?, ?, ?)",
                    (data["name"], data["score"], str(datetime.date.today()))
                )
                db.commit()

            elif msg_type == "get_leaderboard":
                top_scores = db.execute(
                    "SELECT name, score FROM scores ORDER BY score DESC LIMIT 10"
                ).fetchall()
                await client.send(json.dumps({"type": "leaderboard", "scores": top_scores}))
            
            else:
                for c_id, clients in connected_clients.items():
                    if c_id != current_id:
                        await clients.send(json.dumps(data))
                    else: 
                        pass
        
    except websockets.ConnectionClosed:
        print("connection closed!")
    except Exception as e:
        print(f"server:{e}")
    finally:
        connected_clients.pop(current_id)
        
async def main():
    port = int(os.environ.get("PORT",5555))
    async with websockets.serve(client_handler,"0.0.0.0",port):
        print("server is started!")
        print("Waiting for client to connect")
        await asyncio.Future()
        
if __name__ == "__main__":
    asyncio.run(main())
