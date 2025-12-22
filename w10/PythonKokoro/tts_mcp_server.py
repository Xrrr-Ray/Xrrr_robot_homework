from mcp.server.fastmcp import FastMCP

import torch
import os
import time
import soundfile as sf
import sounddevice as sd

from kokoro import KPipeline, KModel

sd.default.device = 11   # 你这台机器的 Realtek 扬声器
# ===================== MCP 初始化 =====================
mcp = FastMCP("tts-server")


# ===================== Kokoro 初始化（只做一次） =====================
KOKORO_DIR = r"D:\PythonModelscope\modelscope_models\AI-ModelScope\Kokoro-82M-v1___1-zh"
repo_id = 'hexgrad/Kokoro-82M-v1.1-zh'

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model_path = os.path.join(KOKORO_DIR, "kokoro-v1_1-zh.pth")
config_path = os.path.join(KOKORO_DIR, "config.json")

print("加载 Kokoro 模型中...")
model = KModel(
    model=model_path,
    config=config_path,
    repo_id=repo_id
).to(device).eval()

# 加载 voice
voice_zf = "zf_001"
voice_zf_tensor = torch.load(
    os.path.join(KOKORO_DIR, "voices", f"{voice_zf}.pt"),
    weights_only=True
)

# 构建 pipeline
zh_pipeline = KPipeline(lang_code='z', repo_id=repo_id, model=model)

print("Kokoro 初始化完成")


# ===================== 语速函数 =====================
def speed_callable(len_ps):
    speed = 0.8
    if len_ps <= 83:
        speed = 1
    elif len_ps < 183:
        speed = 1 - (len_ps - 83) / 500
    return speed * 1.1


# ===================== MCP 工具 =====================
@mcp.tool()
def tts_speak(text: str) -> str:
    """
    使用 Kokoro 将文本转为语音并播放
    """
    print("收到 TTS 请求:", text)

    start_time = time.time()

    generator = zh_pipeline(
        text,
        voice=voice_zf_tensor,
        speed=speed_callable
    )

    result = next(generator)
    wav = result.audio

    # 保存 wav（方便调试）
    wav_path = "output.wav"
    sf.write(wav_path, wav, 24000)

    # 播放前适当放大
    wav = wav * 2.0
    wav = wav.clip(-1.0, 1.0)

    # 播放
    sd.play(wav, 24000)
    sd.wait()

    speech_len = len(wav) / 24000
    rtf = (time.time() - start_time) / speech_len
    print(f"语音播放完成，len={speech_len:.2f}s, rtf={rtf:.2f}")

    return "语音已成功播放"


# ===================== 启动 MCP Server =====================
if __name__ == "__main__":
    print("Kokoro MCP Server started")
    mcp.run()
