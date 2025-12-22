import socket
import asyncio

from mcp_client import MCPClient

HOST = "0.0.0.0"
PORT = 60000   # ASR → MCP 文本端口

TTS_HOST = "127.0.0.1"
TTS_PORT = 60001   # MCP → TTS 文本端口

ACTION_HOST = "172.18.26.112"
ACTION_PORT = 60010

action_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
action_sock.connect((ACTION_HOST, ACTION_PORT))

def send_to_action(action: str):
    action_sock.sendall((action + "\n").encode("utf-8"))

tts_sock = None

def connect_tts():
    global tts_sock
    tts_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tts_sock.connect((TTS_HOST, TTS_PORT))
    print("已连接 TTS Audio Server")

def send_to_tts(text: str):
    if tts_sock is None:
        raise RuntimeError("TTS socket 未连接，请先调用 connect_tts()")
    tts_sock.sendall((text + "\n").encode("utf-8"))


async def main():

    mcp = MCPClient()

    # 连接tts
    connect_tts()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print("MCP Text Server 启动，等待 ASR 文本...")
    conn, addr = server.accept()
    print("ASR 已连接:", addr)

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            text = data.decode("utf-8").strip()
            if not text:
                continue

            print("收到 ASR 文本：", text)

            # 调用大模型
            reply, action= await mcp.process(text)

            if not reply:
                continue

            print("发送给 TTS：", reply)

            # 发给 TTS Audio Server
            send_to_tts(reply)

            if action:
                send_to_action(action)  # 发给机器人动作服务器

    finally:
        conn.close()
        server.close()


if __name__ == "__main__":
    asyncio.run(main())
