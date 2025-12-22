from robot_audio import RobotAudio

if __name__ == "__main__":
    PC_IP = "172.18.24.112"  # PC 的 IP
    audio = RobotAudio(port=50008)   # ⭐ 连 TTS 端口
    audio.receive_audio_client(PC_IP)
