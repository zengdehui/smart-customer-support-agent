# 智能城市生活助手 (Smart City Life Assistant)

一个基于 LangChain 和 OpenAI GPT 构建的智能对话助手，具备查询天气、搜索餐厅和路况等多项城市生活服务能力。
本项目是现代AI智能体（Agent）技术的一个实践示例，采用了LangChain最新的 `create_agent` API 和 LangGraph 状态管理架构。

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![LangChain](https://img.shields.io/badge/LangChain-1.x-orange)]()
<!-- 如果以后有许可证可以加上：[![License](https://img.shields.io/badge/license-MIT-green)]() -->

## ✨ 核心特性

- **🤖 现代智能体架构**：使用 LangChain v1.0+ 官方推荐的 `create_agent` 构建，底层基于 LangGraph 引擎，具备稳健的状态管理和多步推理能力。
- **🔧 多工具集成**：集成多项实用工具，并可轻松扩展：
  - **实时天气查询**：接入和风天气API，提供真实天气数据。
  - **餐厅搜索**：模拟餐厅推荐功能。
  - **路况查询**：模拟实时交通状况查询。
- **💬 连贯对话**：利用检查点（Checkpoint）机制，通过 `thread_id` 维护完整的对话上下文，实现多轮自然交互。
- **🔍 透明化执行**：支持 `debug=True` 模式，可在控制台查看智能体完整的“思考-行动”决策链。

## 🧠 系统架构

本项目清晰地展示了基于状态的现代AI智能体工作流程：

```mermaid
graph TD
     A[用户提问<br>“北京天气如何？”] --> B[智能体接收问题<br>加入消息状态]
    B --> C{LLM核心思考<br>是否需要调用工具？}
    
    C -- 是， 需要查询天气 --> D[生成“工具调用消息”<br>AIMessage: content空, tool_calls有值]
    D --> E[系统执行对应工具<br>get_weather]
    E --> F[工具返回结果<br>ToolMessage]
    F --> B
    
    C -- 否， 或工具结果已就绪 --> G[生成“最终回复消息”<br>AIMessage: content为自然语言]
    G --> H[输出最终答案给用户]