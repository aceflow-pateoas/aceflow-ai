#!/usr/bin/env python3
"""
MCP客户端测试脚本 - 通过标准MCP协议与aceflow-mcp-server通信
"""
import asyncio
import json
import subprocess
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_aceflow_mcp_server():
    """测试aceflow MCP server的所有功能"""
    print("🚀 启动 AceFlow MCP Server 测试...")
    
    # 启动MCP server进程
    server_params = StdioServerParameters(
        command="aceflow-mcp-server",
        args=[],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("✅ MCP连接建立成功")
            
            # 初始化
            await session.initialize()
            print("✅ MCP会话初始化完成")
            
            # 获取可用工具列表
            print("\n📋 获取可用工具列表...")
            tools = await session.list_tools()
            print(f"可用工具数量: {len(tools.tools)}")
            
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n🧪 测试 aceflow_template 工具...")
            # 测试模板工具
            try:
                result = await session.call_tool("aceflow_template", {"action": "list"})
                print("aceflow_template('list') 结果:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(str(content))
            except Exception as e:
                print(f"❌ aceflow_template 测试失败: {e}")
            
            print("\n🧪 测试 aceflow_init 工具...")
            # 测试初始化工具
            try:
                result = await session.call_tool("aceflow_init", {
                    "project_name": "test_project",
                    "project_type": "web"
                })
                print("aceflow_init 结果:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(str(content))
            except Exception as e:
                print(f"❌ aceflow_init 测试失败: {e}")
            
            print("\n🧪 测试 aceflow_stage 工具...")
            # 测试阶段工具
            try:
                result = await session.call_tool("aceflow_stage", {
                    "action": "list"
                })
                print("aceflow_stage('list') 结果:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(str(content))
            except Exception as e:
                print(f"❌ aceflow_stage 测试失败: {e}")
            
            print("\n🧪 测试 aceflow_validate 工具...")
            # 测试验证工具  
            try:
                result = await session.call_tool("aceflow_validate", {
                    "action": "list"
                })
                print("aceflow_validate('list') 结果:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(str(content))
            except Exception as e:
                print(f"❌ aceflow_validate 测试失败: {e}")
                
            print("\n✅ 所有MCP工具测试完成!")

if __name__ == "__main__":
    try:
        asyncio.run(test_aceflow_mcp_server())
        print("\n🎉 AceFlow MCP Server 测试成功完成!")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)