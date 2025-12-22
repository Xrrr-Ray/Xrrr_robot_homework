import soundfile as sf
import numpy as np

wav, sr = sf.read("output.wav")

print("采样率:", sr)
print("最大值:", np.max(np.abs(wav)))
print("均值:", np.mean(wav))
print("前 20 个采样:", wav[:20])
