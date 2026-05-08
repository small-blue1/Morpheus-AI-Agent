import streamlit as st
import json
import requests
from openai import OpenAI

# ==========================================
# 1. 网页设置与初始化
# ==========================================
st.set_page_config(page_title="墨菲斯的极客空间", page_icon="🕶️")
st.title("🕶️ 墨菲斯的极客导师")
st.caption("已挂载 [本地算法] 与 [全网嗅探] 模块...")

MY_SECRET_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # 👉 换上你的智谱 Key
client = OpenAI(api_key=MY_SECRET_KEY, base_url="https://open.bigmodel.cn/api/paas/v4")

if "memory" not in st.session_state:
    st.session_state.memory = [
        {"role": "system",
         "content": "你是一个幽默、说话像黑客帝国里墨菲斯的极客导师。你可以使用工具计算数学题，也可以使用工具抓取网页内容并为用户总结重点。"}
    ]

for msg in st.session_state.memory:
    if msg["role"] in ["user", "assistant"] and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# ==========================================
# 🌟 2. 现实世界的手脚（工具库）
# ==========================================
# 工具 1：数学计算
def calculate_factorial(n: int) -> int:
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


# 工具 2：网页嗅探 (你刚学的爬虫，已修复乱码)
def fetch_webpage(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'  # 👉 解决乱码的魔法
        if response.status_code == 200:
            return response.text[:2000]  # 只取前2000字，防止大模型撑爆
        else:
            return f"访问失败，状态码：{response.status_code}"
    except Exception as e:
        return f"网络异常：{str(e)}"


# 给大模型的说明书（现在有两份说明书了！）
tools_list = [
    {
        "type": "function",
        "function": {
            "name": "calculate_factorial",
            "description": "计算一个数字的阶乘（n!）。",
            "parameters": {
                "type": "object",
                "properties": {"n": {"type": "integer", "description": "需要计算阶乘的整数"}},
                "required": ["n"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "抓取指定URL网址的网页内容，并提取文本。当用户想了解某个网站的信息时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "需要抓取的完整网址，必须以http或https开头"}},
                "required": ["url"]
            }
        }
    }
]

# ==========================================
# 🌟 3. 核心 Agent 思考循环
# ==========================================
user_message = st.chat_input("输入你的指令，比如：帮我看看 https://www.ahszu.edu.cn/ 网站里有什么新闻？")

if user_message:
    with st.chat_message("user"):
        st.write(user_message)
    st.session_state.memory.append({"role": "user", "content": user_message})

    with st.chat_message("assistant"):
        with st.spinner("墨菲斯正在矩阵中调取数据..."):
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=st.session_state.memory,
                tools=tools_list
            )

            ai_message = response.choices[0].message

            # 判断大模型是否决定使用工具
            if ai_message.tool_calls:
                tool_call = ai_message.tool_calls[0]
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # 根据大模型的决定，启动不同的物理工具
                if tool_name == "calculate_factorial":
                    st.info(f"⚡ 启动本地算力：计算 {args['n']} 的阶乘...")
                    tool_result = str(calculate_factorial(args['n']))

                elif tool_name == "fetch_webpage":
                    st.info(f"🌍 启动网络嗅探：潜入 {args['url']} ...")
                    tool_result = fetch_webpage(args['url'])

                # 记录过程并请求最终总结
                st.session_state.memory.append(ai_message.model_dump())
                st.session_state.memory.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

                second_response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=st.session_state.memory
                )
                final_reply = second_response.choices[0].message.content
                st.write(final_reply)
                st.session_state.memory.append({"role": "assistant", "content": final_reply})

            else:
                reply = ai_message.content
                st.write(reply)
                st.session_state.memory.append({"role": "assistant", "content": reply})