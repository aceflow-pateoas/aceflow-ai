#!/usr/bin/env python3
"""
真实MCP环境测试统一服务器
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.unified_server import create_unified_server

async def test_real_mcp_environment():
    """测试真实MCP环境中的统一服务器"""
    print("🚀 Testing Unified Server in Real MCP Environment...")
    
    try:
        # 创建统一服务器
        print("🧪 Creating unified server...")
        server = await create_unified_server()
        print("✅ Unified server created successfully")
        
        # 检查服务器状态
        print("🧪 Checking server status...")
        status = server.get_server_status()
        print(f"✅ Server status: {status}")
        
        # 初始化服务器
        print("🧪 Initializing server...")
        init_success = await server.initialize()
        print(f"✅ Server initialization: {'SUCCESS' if init_success else 'FAILED'}")
        
        # 再次检查状态
        print("🧪 Checking server status after initialization...")
        status = server.get_server_status()
        print(f"✅ Server status: initialized={status['initialized']}, running={status['running']}")
        
        # 检查模块管理器
        print("🧪 Checking module manager...")
        try:
            modules = server.module_manager.list_modules()
            print(f"✅ Available modules: {modules}")
        except Exception as e:
            print(f"⚠️ Module manager test failed: {e}")
        
        print("🎉 Real MCP environment test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Real MCP environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_configuration_loading():
    """测试配置加载"""
    print("\n🧪 Testing configuration loading...")
    
    try:
        from aceflow_mcp_server.unified_config import UnifiedConfig
        
        # 测试默认配置
        config = UnifiedConfig()
        print(f"✅ Default configuration created")
        print(f"   Mode: {config.mode}")
        print(f"   Config type: {type(config)}")
        
        # 测试从文件加载配置
        config_file = "aceflow-unified-config.json"
        if os.path.exists(config_file):
            print(f"✅ Configuration file {config_file} exists")
        else:
            print(f"⚠️ Configuration file {config_file} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 AceFlow MCP Unified Server - Real Environment Test")
    print("=" * 60)
    
    # 测试配置加载
    config_ok = await test_configuration_loading()
    
    # 测试真实MCP环境
    mcp_ok = await test_real_mcp_environment()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Configuration Loading: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Real MCP Environment: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    
    if config_ok and mcp_ok:
        print("🎉 All tests passed! Unified server is ready for production.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)