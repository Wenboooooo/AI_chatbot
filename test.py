import asyncio
import websockets
import json
import sys

async def chat_client():
    uri = "ws://localhost:8001/chat/test_user"
    
    try:
        async with websockets.connect(
            uri,
            ping_interval=None,  # 禁用 ping
            ping_timeout=None,   # 禁用 ping 超时
            close_timeout=None   # 禁用关闭超时
        ) as websocket:
            print("Connected to chat server!")
            print("Type your messages (press Ctrl+C to exit)")
            print("-" * 50)

            while True:
                # 获取用户输入
                message = input("\nYou: ")
                if message.lower() in ['exit', 'quit']:
                    break

                # 发送消息
                await websocket.send(message)

                # 接收并处理服务器响应
                response_complete = False
                print("\nAssistant: ", end="", flush=True)
                
                while not response_complete:
                    response = await websocket.recv()
                    if response == "END_STREAM":
                        response_complete = True
                        print("\n" + "-" * 50)
                        sys.stdout.flush()
                    else:
                        print(response, end="", flush=True)

    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed")
    except KeyboardInterrupt:
        print("\nChat session terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Starting chat client...")
    print("Connecting to WebSocket server...")
    
    try:
        asyncio.run(chat_client())
    except KeyboardInterrupt:
        print("\nChat client terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 