#!/usr/bin/env python3
"""
私有大模型 MCP 适配器
将私有大模型的工具调用转换为 MCP 协议调用
"""

import requests
import json
from typing import Dict, Any, List


class PrivateLLMAdapter:
    """
    私有大模型适配器
    将您的私有LLM（如本地部署的 Qwen、ChatGLM、LLaMA 等）
    的工具调用格式转换为 MCP 协议
    """

    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        """
        初始化适配器

        Args:
            mcp_server_url: MCP Server 的内网地址
        """
        self.mcp_server_url = mcp_server_url
        self.mcp_endpoint = f"{mcp_server_url}/mcp"
        self.session_id = None

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用工具列表，转换为私有大模型的格式

        Returns:
            工具列表（私有大模型格式）
        """
        # 调用 MCP tools/list
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "tools-list",
            "method": "tools/list",
            "params": {}
        }

        response = requests.post(
            self.mcp_endpoint,
            json=mcp_request,
            headers={"Content-Type": "application/json"}
        )

        # 保存会话ID
        self.session_id = response.headers.get("X-Session-ID")

        mcp_tools = response.json()["result"]["tools"]

        # 转换为您的私有大模型的工具格式
        # 这里示例：转换为 OpenAI Function Calling 格式
        converted_tools = []
        for tool in mcp_tools:
            converted_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            })

        return converted_tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        调用工具并返回结果

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        # 构造 MCP tools/call 请求
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"call-{tool_name}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["X-Session-ID"] = self.session_id

        response = requests.post(
            self.mcp_endpoint,
            json=mcp_request,
            headers=headers
        )

        result = response.json()

        if "result" in result:
            # 成功：提取文本内容
            content = result["result"]["content"]
            return content[0]["text"] if content else ""
        elif "error" in result:
            # 错误处理
            error = result["error"]
            return f"Error: {error['message']}"
        else:
            return "Unknown error"

    def process_llm_tool_call(self, llm_tool_call: Dict[str, Any]) -> str:
        """
        处理私有大模型的工具调用请求

        Args:
            llm_tool_call: 私有大模型的工具调用格式，例如：
                {
                    "tool_name": "aceflow_init",
                    "arguments": {
                        "mode": "standard",
                        "project_name": "my-project",
                        "directory": "/path/to/project"
                    }
                }

        Returns:
            工具执行结果
        """
        tool_name = llm_tool_call.get("tool_name") or llm_tool_call.get("name")
        arguments = llm_tool_call.get("arguments") or llm_tool_call.get("parameters")

        return self.call_tool(tool_name, arguments)


# ========== 使用示例 ==========

def example_usage():
    """使用示例：对接私有大模型"""

    # 1. 初始化适配器
    adapter = PrivateLLMAdapter(mcp_server_url="http://192.168.1.100:8000")

    # 2. 获取工具列表，发送给私有大模型
    tools = adapter.get_available_tools()
    print("可用工具：")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

    # 3. 模拟私有大模型决定调用工具
    # 您的私有大模型会返回类似这样的工具调用请求：
    llm_tool_call = {
        "tool_name": "aceflow_init",
        "arguments": {
            "mode": "standard",
            "project_name": "ai-assistant",
            "directory": "/home/user/projects/ai-assistant"
        }
    }

    # 4. 执行工具调用
    result = adapter.process_llm_tool_call(llm_tool_call)
    print(f"\n工具执行结果：")
    print(result)

    # 5. 将结果返回给私有大模型，让它继续生成响应


# ========== FastAPI 集成示例（可选）==========

def create_adapter_api():
    """
    创建一个 FastAPI 服务，作为私有大模型和 MCP Server 之间的桥梁
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    app = FastAPI(title="Private LLM MCP Adapter")
    adapter = PrivateLLMAdapter(mcp_server_url="http://localhost:8000")

    class ToolCallRequest(BaseModel):
        tool_name: str
        arguments: dict

    @app.get("/tools")
    async def get_tools():
        """获取可用工具列表"""
        return adapter.get_available_tools()

    @app.post("/tool-call")
    async def call_tool(request: ToolCallRequest):
        """执行工具调用"""
        try:
            result = adapter.call_tool(request.tool_name, request.arguments)
            return {"success": True, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


if __name__ == "__main__":
    # 示例1: 直接使用适配器
    print("=" * 60)
    print("示例1: 直接使用适配器")
    print("=" * 60)
    example_usage()

    # 示例2: 启动 FastAPI 适配器服务（可选）
    # import uvicorn
    # app = create_adapter_api()
    # uvicorn.run(app, host="0.0.0.0", port=9000)
