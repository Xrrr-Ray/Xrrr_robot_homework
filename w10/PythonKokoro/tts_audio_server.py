import socket
import numpy as np
from kokoro import KPipeline, KModel
import torch
import os
import time

# ================= 音频参数 =================
SAMPLE_RATE = 16000
FRAME_LEN = 960
CHUNK_FRAMES = 10
CHUNK_SIZE = FRAME_LEN * CHUNK_FRAMES

# ================= 端口配置 =================
HOST = "0.0.0.0"
AUDIO_PORT = 50008    # 给机器人发音频
TEXT_PORT = 60001     # 从 MCP 接收文本

CTRL_HOST = "127.0.0.1"
CTRL_PORT = 60002     # 给asr发控制
# ================= Kokoro 初始化 =================
KOKORO_DIR = r"D:\PythonModelscope\modelscope_models\AI-ModelScope\Kokoro-82M-v1___1-zh"
repo_id = "hexgrad/Kokoro-82M-v1.1-zh"
device = "cuda" if torch.cuda.is_available() else "cpu"

voice_zf = "zf_001"
voice_zf_tensor = torch.load(
    os.path.join(KOKORO_DIR, "voices", f"{voice_zf}.pt"),
    weights_only=True
)

model = KModel(
    model=os.path.join(KOKORO_DIR, "kokoro-v1_1-zh.pth"),
    config=os.path.join(KOKORO_DIR, "config.json"),
    repo_id=repo_id
).to(device).eval()

pipeline = KPipeline(lang_code="z", repo_id=repo_id, model=model)


# ================= 文本 socket（MCP） =================
text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_server.bind((HOST, TEXT_PORT))
text_server.listen(1)

print("等待 MCP Text Server 发送文本...")
text_conn, addr = text_server.accept()
print("MCP 已连接:", addr)

# ================= 音频 socket（机器人） =================
audio_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
audio_server.bind((HOST, AUDIO_PORT))
audio_server.listen(1)

print("TTS Audio Server 启动，等待机器人连接...")
audio_conn, addr = audio_server.accept()
print("机器人已连接:", addr)

ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ctrl_sock.connect((CTRL_HOST, CTRL_PORT))
print("已连接 ASR 控制端口")

def speak(text: str):
    notify_asr("START")
    try:
        generator = pipeline(
            text,
            voice=voice_zf_tensor,
            speed=1.2  # ← 加快 20%
        )
        result = next(generator)

        audio = result.audio.detach().cpu().numpy().astype(np.float32)
        audio_int16 = (audio * 32767).astype(np.int16)

        idx = 0
        while idx < len(audio_int16):
            chunk = audio_int16[idx: idx + CHUNK_SIZE]
            audio_conn.sendall(chunk.tobytes())
            idx += CHUNK_SIZE

        play_time = len(audio_int16) / SAMPLE_RATE
    finally:
        time.sleep(play_time + 0.3)
        notify_asr("END")


def notify_asr(cmd: str):
    try:
        ctrl_sock.sendall((cmd + "\n").encode("utf-8"))
    except Exception as e:
        print("通知 ASR 失败：", e)


# ================= 主循环：等文本 → 说话 =================
try:
    while True:
        data = text_conn.recv(4096)
        if not data:
            print("MCP 断开，等待重新连接...")
            text_conn, addr = text_server.accept()
            print("MCP 已重新连接:", addr)
            continue

        text = data.decode("utf-8").strip()
        if not text:
            continue

        print("TTS 收到文本：", text)
        speak(text)

except KeyboardInterrupt:
    print("TTS Server 退出")

finally:
    audio_conn.close()
    text_conn.close()
    audio_server.close()
    text_server.close()
