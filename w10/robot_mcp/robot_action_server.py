import socket
import time

# ===== Tonypi 动作相关 =====
from ActionGroupDict import action_group_dict
import hiwonder.ActionGroupControl as AGC

# ===== 网络配置 =====
HOST = "0.0.0.0"
PORT = 60010   # 动作端口（单独使用）

# ===== 动作映射表 =====
# 规则：action == ActionGroupDict 中的动作名
ACTION_MAP = {
    # 基础
    "stand": "stand",
    "stand_slow": "stand_slow",
    "stand_up_front": "stand_up_front",
    "stand_up_back": "stand_up_back",

    # 移动
    "go_forward": "go_forward",
    "go_forward_fast": "go_forward_fast",
    "back": "back",
    "left_move": "left_move",
    "right_move": "right_move",
    "turn_left": "turn_left",
    "turn_right": "turn_right",
    "stepping": "stepping",

    # 交互
    "wave": "wave",
    "bow": "bow",
    "chest": "chest",
    "twist": "twist",

    # 表演
    "push_ups": "push_ups",
    "sit_ups": "sit_ups",
    "squat": "squat",
    "weightlifting": "weightlifting",

    # 武术
    "left_shot": "left_shot",
    "right_shot": "right_shot",
    "left_uppercut": "left_uppercut",
    "right_uppercut": "right_uppercut",
    "left_kick": "left_kick",
    "right_kick": "right_kick",
    "wing_chun": "wing_chun",

    # ===== 舞蹈（17–24）=====
    "dance_17": "17",
    "dance_18": "18",
    "dance_19": "19",
    "dance_20": "20",
    "dance_21": "21",
    "dance_22": "22",
    "dance_23": "23",
    "dance_24": "24",
}

# ===== 动作执行 =====
def execute_action(action: str):
    """
    action: 动作名（如 wave / bow / stand）
    """
    if action not in ACTION_MAP:
        print(f"⚠️ 未知动作：{action}")
        return

    print(f"🤖 执行动作：{action}")
    AGC.runActionGroup(ACTION_MAP[action])

    # 动作缓冲，防止冲突
    time.sleep(0.2)

# ===== Action Server 主程序 =====
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"✅ Action Server 启动，监听端口 {PORT} ...")

    conn, addr = server.accept()
    print(f"🔗 MCP 已连接：{addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print("❌ MCP 断开连接")
                break

            action = data.decode("utf-8").strip()
            if not action:
                continue

            print("📥 收到动作指令：", action)
            execute_action(action)

    except KeyboardInterrupt:
        print("🛑 Action Server 手动退出")

    finally:
        conn.close()
        server.close()


if __name__ == "__main__":
    main()
