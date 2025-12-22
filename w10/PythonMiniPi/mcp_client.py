import asyncio
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()


class MCPClient:
    def __init__(self):
        self.client = OpenAI()
        self.model = "qwen-max"

        # ===== 支持的动作列表（闭集）=====
        self.actions = {
            # ===== 基础姿态 =====
            "stand": "立正",
            "stand_slow": "慢速立正",
            "stand_up_front": "前倒后起立",
            "stand_up_back": "后倒后起立",

            # ===== 行走 / 移动 =====
            "go_forward": "向前行走",
            "go_forward_fast": "快速向前行走",
            "back": "向后移动",
            "left_move": "向左移动",
            "right_move": "向右移动",
            "turn_left": "向左转",
            "turn_right": "向右转",
            "stepping": "原地踏步",

            # ===== 交互 / 展示 =====
            "wave": "挥手",
            "bow": "鞠躬",
            "chest": "庆祝动作",
            "twist": "扭腰",

            # ===== 体能 / 表演 =====
            "push_ups": "做俯卧撑",
            "sit_ups": "做仰卧起坐",
            "squat": "下蹲",
            "weightlifting": "举重表演",

            # ===== 武术 / 攻击动作 =====
            "left_shot": "左脚踢",
            "right_shot": "右脚踢",
            "left_uppercut": "左勾拳",
            "right_uppercut": "右勾拳",
            "left_kick": "左侧踢",
            "right_kick": "右侧踢",
            "wing_chun": "表演永春拳",

            # ===== 舞蹈动作（17–24）=====
            "dance_17": "舞蹈动作一",
            "dance_18": "舞蹈动作二",
            "dance_19": "舞蹈动作三",
            "dance_20": "舞蹈动作四",
            "dance_21": "舞蹈动作五",
            "dance_22": "舞蹈动作六",
            "dance_23": "舞蹈动作七",
            "dance_24": "舞蹈动作八",

            # ===== 空动作 =====
            "idle": "不做任何动作"
        }

        # ===== System Prompt =====
        self.system_prompt = (
            "你是一个机器人对话与动作决策模块。\n"
            "你需要同时决定：\n"
            "1. 你要说的话（speech）\n"
            "2. 你是否需要做一个动作（action）\n\n"
            "当前机器人支持的动作如下：\n"
        )

        for k, v in self.actions.items():
            self.system_prompt += f"- {k}: {v}\n"

        self.system_prompt += (
            "\n请严格只输出 JSON，不要输出任何多余文字。\n"
            "JSON 格式如下：\n"
            "{\n"
            '  "speech": "你要说的话",\n'
            '  "action": "动作名（只能从上面选择一个）"\n'
            "}\n\n"
            "如果不需要任何动作，请使用 action = idle。"
        )

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    # ===== 返回 (speech, action) =====
    async def process(self, text: str):
        self.messages.append({"role": "user", "content": text})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.3  # 动作决策要稳
        )

        raw_answer = response.choices[0].message.content.strip()
        print("大模型原始输出：", raw_answer)

        try:
            data = json.loads(raw_answer)
            speech = data.get("speech", "")
            action = data.get("action", "idle")
        except Exception as e:
            print("JSON 解析失败：", e)
            speech = raw_answer
            action = "idle"

        # ===== 兜底：防止模型乱返回 =====
        if action not in self.actions:
            action = "idle"

        self.messages.append(
            {"role": "assistant", "content": raw_answer}
        )

        return speech, action


# ===== 手动测试 =====
async def main():
    client = MCPClient()
    while True:
        text = input("你：")
        if text == "exit":
            break
        speech, action = await client.process(text)
        print("回复文本：", speech)
        print("动作指令：", action)


if __name__ == "__main__":
    asyncio.run(main())
