import dashscope
from dashscope import Generation
from typing import Optional, AsyncIterator
import os


class DashScopeClient:
    """阿里百炼大模型客户端"""

    def __init__(self, api_key: str = None, model: str = "qwen-plus"):
        dashscope.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model

    async def call(self, prompt: str, system_prompt: str = None) -> str:
        """同步调用大模型"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = Generation.call(
            model=self.model,
            messages=messages,
            result_format="message",
        )

        if response.status_code != 200:
            raise Exception(f"DashScope API error: {response.code} - {response.message}")

        return response.output.choices[0].message.content

    async def stream_call(
        self, prompt: str, system_prompt: str = None
    ) -> AsyncIterator[str]:
        """流式调用大模型"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = Generation.call(
            model=self.model,
            messages=messages,
            result_format="message",
            stream=True,
        )

        for chunk in response:
            if chunk.status_code == 200:
                yield chunk.output.choices[0].message.content