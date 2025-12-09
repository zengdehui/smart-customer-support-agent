import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from agent_tool import get_weather,get_air_quality


# 确保加载环境变量（通常在文件顶部已有）
load_dotenv()
# 初始化语言模型（LLM）
llm = ChatOpenAI(temperature=0)
# 创建检查点保存器（实现记忆的关键）
memory_saver = MemorySaver()
# 定义智能体的工具
agent_tools = [get_weather,get_air_quality]

# 创建智能体
agent = create_agent(
    model=llm,
    tools=agent_tools,#工具列表
    system_prompt="你是一个专业的天气助手，负责回答用户关于天气和空气质量的问题。",
    checkpointer=memory_saver, #启用，保持对话记忆
    debug=True, #开启调试模式，查看智能体的思考过程
)
# 测试智能体f
def run_test():
    print("="*50)
    print("开始测试智能城市生活助手")
    print("="*50)

    # 📝 测试1：在 user_001 线程中进行多轮对话，观察上下文保持
    print("\n🧪 [测试1] 线程 'user_001' - 多轮对话（上下文保持）")
    config_001 = {"configurable": {"thread_id": "user_001"}}

    # 第一轮：用户查询重庆天气
    question ="重庆今天出门需要带伞吗，空气好不好"
    print(f"\n[用户]: {question}")
    result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config_001)

    # 遍历消息，找到最后一条来自AI且包含实际内容的回复
    for msg in reversed(result['messages']): # 从后往前遍历消息
        if hasattr(msg,'type') and msg.type == 'ai' and msg.content:
            print(f"[ai智能城市生活助手]: {msg.content}")
            break

if __name__ == '__main__':
    run_test()




