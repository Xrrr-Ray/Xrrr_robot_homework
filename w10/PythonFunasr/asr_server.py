import socket
import threading
import numpy as np
from funasr import AutoModel

# ================= 状态 =================
is_speaking = False   # 是否在 TTS 播放中

# ================= 端口配置 =================
AUDIO_HOST = "0.0.0.0"
AUDIO_PORT = 50007

CTRL_HOST = "0.0.0.0"
CTRL_PORT = 60002     # ⭐ 控制端口（START / END）

MCP_HOST = "127.0.0.1"
MCP_PORT = 60000

SAMPLE_RATE = 16000

# ================= 加载 FunASR =================
print("加载 FunpASR 模型中...")
model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 6000},
    disable_update=True
)
print("FunASR 加载完成")

# ================= 连接 MCP =================
text_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_client.connect((MCP_HOST, MCP_PORT))
print("已连接 MCP Text Server")

# ================= 控制线程（接收 START / END） =================
def control_server():
    global is_speaking
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((CTRL_HOST, CTRL_PORT))
    server.listen(1)

    print("ASR 控制端口启动，等待 TTS 连接...")
    conn, _ = server.accept()
    print("TTS 控制通道已连接")

    while True:
        data = conn.recv(1024)
        if not data:
            break

        cmd = data.decode().strip()
        if cmd == "START":
            is_speaking = True
            print("🔇 ASR 静音（TTS 开始）")
        elif cmd == "END":
            is_speaking = False
            print("🎤 ASR 恢复（TTS 结束）")

# ⭐ 启动控制线程
threading.Thread(target=control_server, daemon=True).start()

# ================= 音频接收（Robot → ASR） =================
audio_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
audio_server.bind((AUDIO_HOST, AUDIO_PORT))
audio_server.listen(1)

print("ASR Audio Server 启动，等待机器人连接...")
conn, addr = audio_server.accept()
print("机器人已连接:", addr)

buffer = np.zeros(0, dtype=np.int16)

try:
    while True:
        data = conn.recv(960 * 2)
        if not data:
            break

        audio_chunk = np.frombuffer(data, dtype=np.int16)
        buffer = np.concatenate([buffer, audio_chunk])

        if len(buffer) >= SAMPLE_RATE:

            # ⭐ TTS 期间直接丢弃
            if is_speaking:
                buffer = np.zeros(0, dtype=np.int16)
                continue

            audio_float = buffer.astype(np.float32) / 32768.0
            res = model.generate(input=audio_float, batch_size_s=300)

            if not res:
                buffer = np.zeros(0, dtype=np.int16)
                continue

            text = res[0].get("text", "").strip()
            if not text:
                buffer = np.zeros(0, dtype=np.int16)
                continue

            print("识别结果：", text)
            text_client.sendall(text.encode("utf-8"))

            buffer = np.zeros(0, dtype=np.int16)

except KeyboardInterrupt:
    print("ASR Server 退出")

finally:
    conn.close()
    audio_server.close()
    text_client.close()
