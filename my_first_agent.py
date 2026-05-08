
import streamlit as st
import json
from openai import OpenAI

# ==========================================
# 1. 网页设置与初始化 (没变)
# ==========================================
st.set_page_config(page_title="墨菲斯的极客空间", page_icon="🕶️")
st.color_picker()
st.title("🕶️ 墨菲斯的极客导师")
st.caption("已挂载外部算法模块，随时准备计算...")

MY_SECRET_KEY = "4afd41bb535c4f2db9ff6e0560387ab9.Jou956VXO30o0Sx6"  # 👉 换上你的智谱 Key
client = OpenAI(api_key=MY_SECRET_KEY, base_url="https://open.bigmodel.cn/api/paas/v4")

if "memory" not in st.session_state:
    st.session_state.memory = [
        {"role": "system",
         "content": "你是一个幽默、说话像黑客帝国里墨菲斯的极客导师。当用户问数学问题时，请务必使用你的计算工具。"}
    ]

# 把历史聊天记录画到网页上
for msg in st.session_state.memory:
    if msg["role"] in ["user", "assistant"] and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# ==========================================
# 🌟 2. 定义现实世界的手脚（本地 Python 算法）
# ==========================================
def calculate_factorial(n: int) -> int:
    """极其消耗算力的阶乘算法（比如 5的阶乘 = 5*4*3*2*1）"""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


# 告诉大模型你有这个“手脚”（工具说明书）
tools_list = [
    {
        "type": "function",
        "function": {
            "name": "calculate_factorial",
            "description": "计算一个数字的阶乘（n!）。遇到复杂的数学和阶乘问题时，必须调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "需要计算阶乘的整数，比如 100"}
                },
                "required": ["n"]
            }
        }
    }
]

# ==========================================
# 🌟 3. 核心 Agent 思考循环
# ==========================================
user_message = st.chat_input("输入你想计算的变态数学题，比如：100的阶乘是多少？")

if user_message:
    # (1) 显示用户消息并存入记忆
    with st.chat_message("user"):
        st.write(user_message)
    st.session_state.memory.append({"role": "user", "content": user_message})

    with st.chat_message("assistant"):
        with st.spinner("墨菲斯正在矩阵中思考..."):
            # (2) 带着工具说明书去问大模型
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=st.session_state.memory,
                tools=tools_list  # 👉 关键：把工具递给大模型
            )

            ai_message = response.choices[0].message

            # (3) 判断大模型是否决定使用工具！
            if ai_message.tool_calls:
                # 提取大模型想要调用的工具名称和参数
                tool_call = ai_message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)
                number_to_calc = args['n']

                # 在网页上显示一个炫酷的提示
                st.info(f"⚡ 墨菲斯正在你的电脑上运行算法：计算 {number_to_calc} 的阶乘...")

                # 真正执行你电脑上的 Python 算法！
                math_result = calculate_factorial(number_to_calc)

                # (4) 把大模型的请求和我们算出的结果，都存进记忆里
                st.session_state.memory.append(ai_message.model_dump())  # 存入模型的调用请求
                st.session_state.memory.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(math_result)  # 存入本地算出的真实结果
                })

                # (5) 把结果发给大模型，让它做最终的总结
                second_response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=st.session_state.memory
                )
                final_reply = second_response.choices[0].message.content
                st.write(final_reply)
                st.session_state.memory.append({"role": "assistant", "content": final_reply})

            else:
                # 如果是普通聊天，直接回答
                reply = ai_message.content
                st.write(reply)
                st.session_state.memory.append({"role": "assistant", "content": reply})