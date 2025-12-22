import asyncio
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() # 读进.env里的环境变量


# ====== 模型配置（最小版） ======
class Model:
    def __init__(self):
        self.client = OpenAI() # OpenAI初始化，实际请求地址由 OPENAI_BASE_URL 决定
        self.model_name = "qwen-max"   # 根据你自己的 Qwen 模型名调整


# ====== 最小可运行 Client ======
class MCPClient:
    def __init__(self):
        self.model = Model()
        self.messages = [
            {
                "role": "system",
                "content": "你是一个机器人，用中文回答，尽量简短。"
            }
        ]

    async def process_query(self, query: str) -> str: # 用户输入
        self.messages.append({
            "role": "user",
            "content": query
        })

        response = self.model.client.chat.completions.create( # 调用大模型，模型在这里完成了：理解上下文、推理、生成回复文本
            model=self.model.model_name,
            messages=self.messages,
            extra_body={"enable_thinking": False}
        )

        reply = response.choices[0].message.content # 模型回复

        self.messages.append({ # 模型输出
            "role": "assistant",
            "content": reply
        })

        return reply


# ====== 主函数 ======
async def main():
    client = MCPClient()
    print("机器人已启动，输入 exit 退出。")

    while True:
        user_input = input("你：")
        if user_input.strip().lower() == "exit":
            break

        reply = await client.process_query(user_input)
        print("机器人：", reply)


if __name__ == "__main__":
    asyncio.run(main())
