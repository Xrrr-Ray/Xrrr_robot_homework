from funasr import AutoModel

model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
)
wav_path = "test1.wav"  # 你的 16k wav 文件路径



res = model.generate(
    input=wav_path,
    batch_size_s=0
)

print(res[0]["text"])
