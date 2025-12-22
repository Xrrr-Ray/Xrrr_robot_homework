import torch
import os
import time
from kokoro import KPipeline, KModel
import soundfile as sf
KOKORO_DIR = r"D:\PythonModelscope\modelscope_models\AI-ModelScope\Kokoro-82M-v1___1-zh"
voice_zf = "zf_001"
voice_zf_tensor = torch.load(
    os.path.join(KOKORO_DIR, "voices", f"{voice_zf}.pt"),
    weights_only=True
)

voice_af = "af_maple"
voice_af_tensor = torch.load(
    os.path.join(KOKORO_DIR, "voices", f"{voice_af}.pt"),
    weights_only=True
)
repo_id = 'hexgrad/Kokoro-82M-v1.1-zh'

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model_path = os.path.join(KOKORO_DIR, "kokoro-v1_1-zh.pth")

config_path = os.path.join(KOKORO_DIR, "config.json")

model = KModel(model=model_path, config=config_path, repo_id=repo_id).to(device).eval()


def speed_callable(len_ps):
    speed = 0.8
    if len_ps <= 83:
        speed = 1
    elif len_ps < 183:
        speed = 1 - (len_ps - 83) / 500
    return speed * 1.1


zh_pipeline = KPipeline(lang_code='z', repo_id=repo_id, model=model)
sentence = '你好，这是一个语音合成测试。'
start_time = time.time()
generator = zh_pipeline(sentence, voice=voice_zf_tensor, speed=speed_callable)
result = next(generator)
wav = result.audio
speech_len = len(wav) / 24000
print('yield speech len {}, rtf {}'.format(speech_len, (time.time() - start_time) / speech_len))
sf.write('output.wav', wav, 24000)