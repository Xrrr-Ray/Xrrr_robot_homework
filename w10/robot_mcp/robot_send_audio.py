from robot_audio import RobotAudio

if __name__ == "__main__":
    PC_IP = "172.18.24.112"   # ⚠️ 改成你 PC 的局域网 IP
    audio = RobotAudio()
    audio.send_audio_client(PC_IP)
