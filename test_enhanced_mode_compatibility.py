#!/usr/bin/env python3
"""
增强模式兼容性测试
Enhanced Mode Compatibility Test

测试统一服务器在增强模式下的协作功能兼容性
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.unified_server import create_unified_server
from aceflow_mcp_server.unified_config import UnifiedConfig

async def test_enhanced_mode():
    """测试增强模式下的功能"""
    print("🚀 Testing Enhanced Mode Compatibility...")
    
    try:
        # 创建增强模式配置
        enhanced_config = UnifiedConfig(mode="enhanced")
        print(f"✅ Enhanced config created: {enhanced_config.mode}")
        
        # 创建统一服务器，使用运行时覆盖来设置增强模式
        server = await create_unified_server(runtime_overrides={"mode": "enhanced"})
        await server.initialize()
        
        print("✅ Enhanced server initialized")
        
        # 检查服务器状态
        status = server.get_server_status()
        print(f"✅ Server status: initialized={status['initialized']}")
        print(f"✅ Server config mode: {status['config']['mode']}")
        print(f"✅ Server features: {status['config']['features']}")
        
        # 检查实际配置
        actual_config = server.config
        print(f"✅ Actual config mode: {actual_config.mode}")
        print(f"✅ Collaboration enabled: {actual_config.collaboration.enabled}")
        print(f"✅ Intelligence enabled: {actual_config.intelligence.enabled}")
        
        # 检查模块
        modules = server.module_manager.list_modules()
        print(f"✅ Available modules: {modules}")
        
        # 测试协作模块
        if "collaboration" in modules:
            collaboration_module = server.module_manager.get_module("collaboration")
            print("✅ Collaboration module loaded")
            
            # 测试协作工具
            collaboration_tools = ["aceflow_respond", "aceflow_collaboration_status", "aceflow_task_execute"]
            for tool_name in collaboration_tools:
                if hasattr(collaboration_module, tool_name):
                    print(f"  ✅ Tool {tool_name} available")
                else:
                    print(f"  ❌ Tool {tool_name} not found")
        else:
            print("⚠️ Collaboration module not loaded in enhanced mode")
        
        # 测试智能模块
        if "intelligence" in modules:
            intelligence_module = server.module_manager.get_module("intelligence")
            print("✅ Intelligence module loaded")
            
            # 测试智能工具
            intelligence_tools = ["aceflow_intent_analyze", "aceflow_recommend"]
            for tool_name in intelligence_tools:
                if hasattr(intelligence_module, tool_name):
                    print(f"  ✅ Tool {tool_name} available")
                else:
                    print(f"  ❌ Tool {tool_name} not found")
        else:
            print("⚠️ Intelligence module not loaded in enhanced mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 AceFlow MCP Server - Enhanced Mode Compatibility Test")
    print("=" * 60)
    
    success = await test_enhanced_mode()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Enhanced mode compatibility test PASSED!")
        return 0
    else:
        print("❌ Enhanced mode compatibility test FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)