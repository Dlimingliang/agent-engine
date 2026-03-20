import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import ToolRegistry
from dotenv import load_dotenv
from openai import OpenAI
from typing import Any
from .message import user_message, assistant_message, tool_message, system_message
from trace import Tracer
from pydantic import BaseModel

# 加载 .env 文件中的环境变量
load_dotenv()


class TaskResult(BaseModel):
    """任务执行结果"""
    success: bool  # 是否成功
    answer: str    # 给用户的答案


# === AI Generated Code Start matthewmli ===
# PromptComposer 和 RuleEngine 由用户自行实现
# === AI Generated Code End matthewmli ===


class Agent:
    def __init__(self, name: str, role: str, system_prompt: str, tool_registry: ToolRegistry):
        self.name = name
        self.role = role
        self.tool_registry = tool_registry
        self.MaxRecursion = 10
        self.model = os.getenv("LLM_MODEL_ID")
        apiKey = os.getenv("LLM_API_KEY")
        baseUrl = os.getenv("LLM_BASE_URL")
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=60)
        self.history = [system_message(system_prompt)]

    def chat(self, messages: list[dict[str, Any]], temperature: float = 0, stream=False, require_json=False):
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        params = {
            "model": self.model,
            "messages": messages,
            "tools": self.tool_registry.get_openai_tools(),
            "temperature": temperature,
            "stream": stream,
        }

        if require_json:
            params["response_format"] = {"type": "json_object"}
        try:
            response = self.client.chat.completions.create(**params)
            print("✅ 大语言模型响应成功:")
            return response
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return ""

    def process(self, session_id: str, user_input: str) -> TaskResult | None:
        tracer = Tracer(session_id)
        # 用户消息放入会话消息和trace
        self.history.append(user_message(user_input))
        tracer.log_user_input(user_input)

        try:
            # 自循环
            count = 0
            while count < self.MaxRecursion:
                count += 1
                # 调用大模型
                tracer.start_timer()
                response = self.chat(self.get_messages())
                message = response.choices[0].message
                print(f"🤖 Assistant response: {message}")
                # 模型返回放入会话消息和trace
                tracer.log_llm_call(messages=self.get_messages(), response=message, duration_ms=tracer._get_duration_ms())
                self.history.append(assistant_message(content=message.content, tool_calls=message.tool_calls))
                # 如果存在工具调用调用工具
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_id = tool_call.id
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # === AI Generated Code Start matthewmli ===
                        # TODO: 在执行工具前，使用 RuleEngine 检查是否合规
                        # === AI Generated Code End matthewmli ===
                        
                        # 执行工具调用
                        tracer.start_timer()
                        tool_res = self.tool_registry.execute(tool_name, tool_args)
                        # 工具调用放入会话消息和trace
                        self.history.append(tool_message(tool_id, tool_res, tool_name))
                        tracer.log_tool_call(tool_name=tool_name, arguments=tool_args, result=tool_res, duration_ms=tracer._get_duration_ms())
                    continue
                # 没有工具返回结果

                final_response = self.chat(self.get_messages(), require_json=True)
                final_content = final_response.choices[0].message.content
                tracer.log_final_output(final_content)
                print(f"tracer: {tracer.summary()}")
                result = TaskResult.model_validate_json(final_content)
                return result

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            tracer.log_error(str(e))
            return None

    def get_messages(self) -> list[dict[str, Any]]:
        messages = []
        for message in self.history:
            messages.append(message.to_openai_dict())
        return messages
