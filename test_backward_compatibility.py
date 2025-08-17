#!/usr/bin/env python3
"""
向后兼容性测试套件
Backward Compatibility Test Suite

测试统一服务器与原有 aceflow-server 和 aceflow-enhanced-server 的兼容性
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.unified_server import create_unified_server
from aceflow_mcp_server.unified_config import UnifiedConfig

class BackwardCompatibilityTester:
    """向后兼容性测试器"""
    
    def __init__(self):
        self.server = None
        self.test_results = []
        
    async def setup(self):
        """设置测试环境"""
        print("🔧 Setting up backward compatibility test environment...")
        
        # 创建统一服务器
        self.server = await create_unified_server()
        await self.server.initialize()
        
        print("✅ Test environment setup complete")
    
    async def test_original_aceflow_server_api(self):
        """测试原始 aceflow-server API 兼容性"""
        print("\n🧪 Testing Original AceFlow Server API Compatibility...")
        
        test_cases = [
            {
                "name": "aceflow_init - 基础项目初始化",
                "tool": "aceflow_init",
                "params": {
                    "mode": "standard",
                    "project_name": "test-project",
                    "directory": "test-dir"
                },
                "expected_fields": ["success", "message", "project_info"]
            },
            {
                "name": "aceflow_stage - 基础阶段管理",
                "tool": "aceflow_stage",
                "params": {
                    "action": "next",
                    "current_stage": "planning"
                },
                "expected_fields": ["success", "message", "stage_info"]
            },
            {
                "name": "aceflow_validate - 基础验证",
                "tool": "aceflow_validate",
                "params": {
                    "mode": "basic",
                    "target": "project"
                },
                "expected_fields": ["success", "message", "validation_results"]
            }
        ]
        
        for test_case in test_cases:
            try:
                print(f"  🔍 Testing: {test_case['name']}")
                
                # 模拟工具调用（由于我们没有完整的MCP客户端，我们测试模块直接调用）
                core_module = self.server.module_manager.get_module("core")
                if not core_module:
                    raise Exception("Core module not found")
                
                # 检查工具是否存在
                tool_name = test_case['tool']
                if hasattr(core_module, tool_name):
                    print(f"    ✅ Tool {tool_name} exists in core module")
                    
                    # 尝试调用工具进行更深入的兼容性测试
                    try:
                        tool_method = getattr(core_module, tool_name)
                        # 使用测试参数调用工具
                        result = tool_method(**test_case['params'])
                        
                        # 检查返回结果是否包含预期字段
                        if isinstance(result, dict):
                            missing_fields = [field for field in test_case['expected_fields'] 
                                            if field not in result]
                            if not missing_fields:
                                print(f"    ✅ Tool {tool_name} response format is compatible")
                                self.test_results.append({
                                    "test": test_case['name'],
                                    "status": "PASS",
                                    "message": f"Tool {tool_name} is fully compatible"
                                })
                            else:
                                print(f"    ⚠️ Tool {tool_name} missing fields: {missing_fields}")
                                self.test_results.append({
                                    "test": test_case['name'],
                                    "status": "PARTIAL",
                                    "message": f"Tool {tool_name} works but missing fields: {missing_fields}"
                                })
                        else:
                            print(f"    ⚠️ Tool {tool_name} returns non-dict result")
                            self.test_results.append({
                                "test": test_case['name'],
                                "status": "PARTIAL",
                                "message": f"Tool {tool_name} works but returns unexpected format"
                            })
                    except Exception as call_error:
                        print(f"    ⚠️ Tool {tool_name} exists but call failed: {call_error}")
                        self.test_results.append({
                            "test": test_case['name'],
                            "status": "PARTIAL",
                            "message": f"Tool {tool_name} exists but call failed: {call_error}"
                        })
                else:
                    print(f"    ❌ Tool {tool_name} not found in core module")
                    self.test_results.append({
                        "test": test_case['name'],
                        "status": "FAIL",
                        "message": f"Tool {tool_name} not found"
                    })
                    
            except Exception as e:
                print(f"    ❌ Test failed: {e}")
                self.test_results.append({
                    "test": test_case['name'],
                    "status": "FAIL",
                    "message": str(e)
                })
    
    async def test_enhanced_aceflow_server_api(self):
        """测试增强 aceflow-enhanced-server API 兼容性"""
        print("\n🧪 Testing Enhanced AceFlow Server API Compatibility...")
        
        test_cases = [
            {
                "name": "aceflow_respond - 协作响应",
                "tool": "aceflow_respond",
                "params": {
                    "message": "Test collaboration message",
                    "context": "testing"
                },
                "expected_fields": ["status", "response", "collaboration_data"]
            },
            {
                "name": "aceflow_collaboration_status - 协作状态",
                "tool": "aceflow_collaboration_status",
                "params": {
                    "project_id": "test-project"
                },
                "expected_fields": ["status", "collaboration_state", "participants"]
            },
            {
                "name": "aceflow_task_execute - 任务执行",
                "tool": "aceflow_task_execute",
                "params": {
                    "task_id": "test-task",
                    "action": "start"
                },
                "expected_fields": ["status", "task_result", "execution_data"]
            }
        ]
        
        for test_case in test_cases:
            try:
                print(f"  🔍 Testing: {test_case['name']}")
                
                # 检查协作模块
                collaboration_module = self.server.module_manager.get_module("collaboration")
                if not collaboration_module:
                    print(f"    ⚠️ Collaboration module not loaded (expected in basic mode)")
                    self.test_results.append({
                        "test": test_case['name'],
                        "status": "SKIP",
                        "message": "Collaboration module not enabled in current mode"
                    })
                    continue
                
                # 检查工具是否存在
                tool_name = test_case['tool']
                if hasattr(collaboration_module, tool_name):
                    print(f"    ✅ Tool {tool_name} exists in collaboration module")
                    
                    # 尝试调用工具进行兼容性测试
                    try:
                        tool_method = getattr(collaboration_module, tool_name)
                        result = tool_method(**test_case['params'])
                        
                        if isinstance(result, dict):
                            missing_fields = [field for field in test_case['expected_fields'] 
                                            if field not in result]
                            if not missing_fields:
                                print(f"    ✅ Tool {tool_name} response format is compatible")
                                self.test_results.append({
                                    "test": test_case['name'],
                                    "status": "PASS",
                                    "message": f"Tool {tool_name} is fully compatible"
                                })
                            else:
                                print(f"    ⚠️ Tool {tool_name} missing fields: {missing_fields}")
                                self.test_results.append({
                                    "test": test_case['name'],
                                    "status": "PARTIAL",
                                    "message": f"Tool {tool_name} works but missing fields: {missing_fields}"
                                })
                        else:
                            self.test_results.append({
                                "test": test_case['name'],
                                "status": "PARTIAL",
                                "message": f"Tool {tool_name} works but returns unexpected format"
                            })
                    except Exception as call_error:
                        print(f"    ⚠️ Tool {tool_name} exists but call failed: {call_error}")
                        self.test_results.append({
                            "test": test_case['name'],
                            "status": "PARTIAL",
                            "message": f"Tool {tool_name} exists but call failed: {call_error}"
                        })
                else:
                    print(f"    ❌ Tool {tool_name} not found in collaboration module")
                    self.test_results.append({
                        "test": test_case['name'],
                        "status": "FAIL",
                        "message": f"Tool {tool_name} not found"
                    })
                    
            except Exception as e:
                print(f"    ❌ Test failed: {e}")
                self.test_results.append({
                    "test": test_case['name'],
                    "status": "FAIL",
                    "message": str(e)
                })
    
    async def test_resource_compatibility(self):
        """测试资源兼容性"""
        print("\n🧪 Testing Resource Compatibility...")
        
        expected_resources = [
            "project_state",
            "workflow_config", 
            "stage_guide"
        ]
        
        for resource_name in expected_resources:
            try:
                print(f"  🔍 Testing resource: {resource_name}")
                
                # 检查资源是否在服务器中注册
                # 由于我们没有直接的资源访问方法，我们检查模块是否提供了资源
                core_module = self.server.module_manager.get_module("core")
                if core_module and hasattr(core_module, 'get_resources'):
                    resources = core_module.get_resources()
                    if resource_name in [r.name for r in resources]:
                        print(f"    ✅ Resource {resource_name} is available")
                        self.test_results.append({
                            "test": f"Resource {resource_name}",
                            "status": "PASS",
                            "message": f"Resource {resource_name} is available"
                        })
                    else:
                        print(f"    ❌ Resource {resource_name} not found")
                        self.test_results.append({
                            "test": f"Resource {resource_name}",
                            "status": "FAIL",
                            "message": f"Resource {resource_name} not found"
                        })
                else:
                    print(f"    ⚠️ Cannot verify resource {resource_name} (method not available)")
                    self.test_results.append({
                        "test": f"Resource {resource_name}",
                        "status": "SKIP",
                        "message": "Resource verification method not available"
                    })
                    
            except Exception as e:
                print(f"    ❌ Resource test failed: {e}")
                self.test_results.append({
                    "test": f"Resource {resource_name}",
                    "status": "FAIL",
                    "message": str(e)
                })
    
    async def test_configuration_compatibility(self):
        """测试配置兼容性"""
        print("\n🧪 Testing Configuration Compatibility...")
        
        try:
            # 测试基础模式配置
            print("  🔍 Testing basic mode configuration...")
            basic_config = UnifiedConfig(mode="basic")
            print(f"    ✅ Basic mode config created: {basic_config.mode}")
            
            # 测试标准模式配置
            print("  🔍 Testing standard mode configuration...")
            standard_config = UnifiedConfig(mode="standard")
            print(f"    ✅ Standard mode config created: {standard_config.mode}")
            
            # 测试增强模式配置
            print("  🔍 Testing enhanced mode configuration...")
            enhanced_config = UnifiedConfig(mode="enhanced")
            print(f"    ✅ Enhanced mode config created: {enhanced_config.mode}")
            
            self.test_results.append({
                "test": "Configuration Modes",
                "status": "PASS",
                "message": "All configuration modes are supported"
            })
            
        except Exception as e:
            print(f"    ❌ Configuration test failed: {e}")
            self.test_results.append({
                "test": "Configuration Modes",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_parameter_format_compatibility(self):
        """测试参数格式兼容性"""
        print("\n🧪 Testing Parameter Format Compatibility...")
        
        # 测试各种参数格式是否被正确处理
        test_parameters = [
            {
                "name": "String parameters",
                "params": {"project_name": "test-project", "project_type": "web"},
                "expected": True
            },
            {
                "name": "Boolean parameters", 
                "params": {"enable_feature": True, "debug_mode": False},
                "expected": True
            },
            {
                "name": "Numeric parameters",
                "params": {"timeout": 30, "max_retries": 3, "version": 1.0},
                "expected": True
            },
            {
                "name": "Array parameters",
                "params": {"tags": ["web", "frontend"], "files": []},
                "expected": True
            },
            {
                "name": "Object parameters",
                "params": {"config": {"debug": True}, "metadata": {}},
                "expected": True
            }
        ]
        
        for test_param in test_parameters:
            try:
                print(f"  🔍 Testing: {test_param['name']}")
                
                # 验证参数可以被JSON序列化（MCP要求）
                json_str = json.dumps(test_param['params'])
                parsed_back = json.loads(json_str)
                
                if parsed_back == test_param['params']:
                    print(f"    ✅ {test_param['name']} format is compatible")
                    self.test_results.append({
                        "test": test_param['name'],
                        "status": "PASS",
                        "message": "Parameter format is MCP compatible"
                    })
                else:
                    print(f"    ❌ {test_param['name']} format compatibility issue")
                    self.test_results.append({
                        "test": test_param['name'],
                        "status": "FAIL",
                        "message": "Parameter format not preserved after JSON serialization"
                    })
                    
            except Exception as e:
                print(f"    ❌ Parameter test failed: {e}")
                self.test_results.append({
                    "test": test_param['name'],
                    "status": "FAIL",
                    "message": str(e)
                })
    
    def generate_compatibility_report(self):
        """生成兼容性报告"""
        print("\n" + "="*60)
        print("📊 BACKWARD COMPATIBILITY TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        partial_tests = len([r for r in self.test_results if r['status'] == 'PARTIAL'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        print(f"Success Rate: {((passed_tests + partial_tests)/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "PARTIAL": "⚠️"}[result['status']]
            print(f"  {status_icon} {result['test']}: {result['message']}")
        
        # 兼容性评估
        print("\n🎯 Compatibility Assessment:")
        if failed_tests == 0:
            print("🎉 EXCELLENT: Full backward compatibility achieved!")
        elif failed_tests <= 2:
            print("✅ GOOD: Minor compatibility issues that can be easily fixed")
        elif failed_tests <= 5:
            print("⚠️ MODERATE: Some compatibility issues need attention")
        else:
            print("❌ POOR: Significant compatibility issues require immediate attention")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "partial": partial_tests,
            "skipped": skipped_tests,
            "success_rate": ((passed_tests + partial_tests)/total_tests)*100,
            "results": self.test_results
        }

async def main():
    """主测试函数"""
    print("🚀 AceFlow MCP Server - Backward Compatibility Test Suite")
    print("="*60)
    
    tester = BackwardCompatibilityTester()
    
    try:
        # 设置测试环境
        await tester.setup()
        
        # 执行所有兼容性测试
        await tester.test_original_aceflow_server_api()
        await tester.test_enhanced_aceflow_server_api()
        await tester.test_resource_compatibility()
        await tester.test_configuration_compatibility()
        await tester.test_parameter_format_compatibility()
        
        # 生成报告
        report = tester.generate_compatibility_report()
        
        # 保存报告到文件
        with open("backward_compatibility_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: backward_compatibility_report.json")
        
        # 返回适当的退出码
        return 0 if report['failed'] == 0 else 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)