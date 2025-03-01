import asyncio
import websockets




async def chat():
    # uri = "ws://localhost:8000/chat/user123"
    uri = "ws://localhost:8001/chat/user123"
    async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as websocket:  
        print("Connected to WebSocket server. Type 'exit' to quit.")

        while True:
            user_message = input("You: ")
            if user_message.lower() == "exit":
                break

            await websocket.send(user_message)

            print("Assistant: ", end="", flush=True)
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=500)

                    if response == "PING":  # **忽略心跳**
                        continue
                    elif response == "END_STREAM":
                        break  # **立即退出等待**
                    
                    print(response, end="", flush=True)

                except asyncio.TimeoutError:
                    print("\nNo response from server, connection might be lost.")
                    break

            print()

asyncio.run(chat())