#!/usr/bin/env python3
"""
AceFlow MCP服务器测试脚本
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_aceflow_server():
    """测试AceFlow MCP服务器"""
    print("🧪 测试AceFlow MCP服务器...")
    
    try:
        # 创建服务器参数
        server_params = StdioServerParameters(
            command="aceflow-enhanced-server",
            args=["--log-level", "INFO"]
        )
        
        # 连接服务器
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()
                
                # 列出工具
                tools = await session.list_tools()
                print(f"✅ 发现 {len(tools.tools)} 个工具:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # 列出资源
                resources = await session.list_resources()
                print(f"✅ 发现 {len(resources.resources)} 个资源:")
                for resource in resources.resources:
                    print(f"   - {resource.name}: {resource.description}")
                
                # 测试协作状态工具
                print("\n🔧 测试协作状态工具...")
                result = await session.call_tool(
                    "aceflow_collaboration_status",
                    {}
                )
                print(f"✅ 协作状态工具响应: {result.content[0].text}")
                
                print("\n🎉 所有测试通过！")
                return True
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_aceflow_server())
