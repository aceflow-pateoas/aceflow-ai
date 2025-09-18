#!/usr/bin/env python3
"""
AceFlow MCP Server HTTP模式功能测试脚本
测试HTTP传输模式的各项功能
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPHTTPTester:
    """MCP HTTP服务器测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/mcp"
        self.health_endpoint = f"{base_url}/health"
        self.session_id = None
        
    async def test_health_check(self) -> bool:
        """测试健康检查端点"""
        logger.info("🔍 测试健康检查...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.health_endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ 健康检查通过: {data}")
                    return True
                else:
                    logger.error(f"❌ 健康检查失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 健康检查异常: {e}")
            return False
    
    async def test_mcp_initialize(self) -> bool:
        """测试MCP初始化"""
        logger.info("🚀 测试MCP初始化...")
        
        message = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "AceFlow Test Client",
                    "version": "1.0.0"
                }
            }
        }
        
        return await self._send_mcp_message(message)
    
    async def test_tools_list(self) -> bool:
        """测试工具列表"""
        logger.info("📋 测试工具列表...")
        
        message = {
            "jsonrpc": "2.0",
            "id": "tools-1", 
            "method": "tools/list",
            "params": {}
        }
        
        return await self._send_mcp_message(message)
    
    async def test_tool_call(self) -> bool:
        """测试工具调用"""
        logger.info("🔧 测试工具调用...")
        
        message = {
            "jsonrpc": "2.0",
            "id": "call-1",
            "method": "tools/call",
            "params": {
                "name": "aceflow_validate",
                "arguments": {
                    "mode": "basic",
                    "fix": False,
                    "report": True
                }
            }
        }
        
        return await self._send_mcp_message(message)
    
    async def _send_mcp_message(self, message: Dict[str, Any]) -> bool:
        """发送MCP消息"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            if self.session_id:
                headers["X-Session-ID"] = self.session_id
            
            async with httpx.AsyncClient() as client:
                # 发送POST请求
                response = await client.post(
                    self.mcp_endpoint,
                    json=message,
                    headers=headers
                )
                
                # 检查响应状态
                if response.status_code == 202:
                    data = response.json()
                    logger.info(f"✅ 消息发送成功: {data}")
                    
                    # 获取会话ID
                    if "session_id" in data:
                        self.session_id = data["session_id"]
                    
                    return True
                else:
                    logger.error(f"❌ 消息发送失败: {response.status_code}, {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 发送消息异常: {e}")
            return False
    
    async def test_sse_stream(self) -> bool:
        """测试Server-Sent Events流"""
        logger.info("🌊 测试SSE流...")
        
        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            if self.session_id:
                headers["X-Session-ID"] = self.session_id
            
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", self.mcp_endpoint, headers=headers) as response:
                    if response.status_code != 200:
                        logger.error(f"❌ SSE流连接失败: {response.status_code}")
                        return False
                    
                    logger.info("✅ SSE流连接成功")
                    
                    # 读取几个事件
                    event_count = 0
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            try:
                                data = json.loads(line[5:].strip())
                                logger.info(f"📨 收到SSE事件: {data}")
                                event_count += 1
                                
                                if event_count >= 3:  # 读取3个事件后退出
                                    break
                            except json.JSONDecodeError:
                                logger.debug(f"非JSON数据: {line}")
                        elif line.startswith("event:"):
                            logger.debug(f"事件类型: {line[6:].strip()}")
                    
                    logger.info(f"✅ SSE流测试完成，共收到 {event_count} 个事件")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ SSE流测试异常: {e}")
            return False
    
    async def test_concurrent_requests(self) -> bool:
        """测试并发请求"""
        logger.info("🔄 测试并发请求...")
        
        messages = []
        for i in range(5):
            messages.append({
                "jsonrpc": "2.0",
                "id": f"concurrent-{i}",
                "method": "tools/list",
                "params": {}
            })
        
        try:
            # 并发发送消息
            tasks = [self._send_mcp_message(msg) for msg in messages]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if r is True)
            logger.info(f"✅ 并发测试完成: {success_count}/{len(messages)} 成功")
            
            return success_count >= len(messages) // 2  # 至少一半成功
            
        except Exception as e:
            logger.error(f"❌ 并发测试异常: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        logger.info("🚀 开始AceFlow MCP HTTP功能测试")
        
        tests = [
            ("健康检查", self.test_health_check),
            ("MCP初始化", self.test_mcp_initialize),
            ("工具列表", self.test_tools_list),
            ("工具调用", self.test_tool_call),
            ("SSE流", self.test_sse_stream),
            ("并发请求", self.test_concurrent_requests),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                logger.info(f"\n📋 执行测试: {test_name}")
                result = await test_func()
                results.append((test_name, result))
                
                if result:
                    logger.info(f"✅ {test_name} 测试通过")
                else:
                    logger.error(f"❌ {test_name} 测试失败")
                    
            except Exception as e:
                logger.error(f"❌ {test_name} 测试异常: {e}")
                results.append((test_name, False))
        
        # 汇总结果
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        logger.info(f"\n🎯 测试汇总: {passed}/{total} 通过")
        
        for test_name, result in results:
            status = "✅" if result else "❌"
            logger.info(f"  {status} {test_name}")
        
        return passed == total


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AceFlow MCP HTTP功能测试")
    parser.add_argument("--url", default="http://localhost:8000", help="服务器URL")
    parser.add_argument("--test", choices=["health", "init", "tools", "call", "sse", "concurrent", "all"], 
                       default="all", help="运行特定测试")
    args = parser.parse_args()
    
    tester = MCPHTTPTester(args.url)
    
    if args.test == "all":
        success = await tester.run_all_tests()
    else:
        test_methods = {
            "health": tester.test_health_check,
            "init": tester.test_mcp_initialize,
            "tools": tester.test_tools_list,
            "call": tester.test_tool_call,
            "sse": tester.test_sse_stream,
            "concurrent": tester.test_concurrent_requests,
        }
        
        success = await test_methods[args.test]()
    
    if success:
        logger.info("🎉 所有测试通过!")
        exit(0)
    else:
        logger.error("💥 部分测试失败!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())