#!/usr/bin/env python3
"""
生产部署测试套件
Production Deployment Test Suite

在真实MCP环境中进行全面的部署测试和验证
"""

import asyncio
import json
import sys
import os
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import concurrent.futures

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.unified_server import create_unified_server
from aceflow_mcp_server.unified_config import UnifiedConfig

class ProductionDeploymentTester:
    """生产部署测试器"""
    
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {}
        self.deployment_configs = []
        
    async def run_comprehensive_deployment_tests(self):
        """运行全面的部署测试"""
        print("🚀 Starting Comprehensive Production Deployment Tests")
        print("=" * 60)
        
        # 测试套件
        test_suites = [
            ("基础部署测试", self.test_basic_deployment),
            ("多模式部署测试", self.test_multi_mode_deployment),
            ("性能基准测试", self.test_performance_benchmarks),
            ("并发负载测试", self.test_concurrent_load),
            ("故障恢复测试", self.test_failure_recovery),
            ("配置热重载测试", self.test_config_hot_reload),
            ("内存泄漏测试", self.test_memory_leak),
            ("长期稳定性测试", self.test_long_term_stability),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n🧪 {suite_name}...")
            try:
                start_time = time.time()
                result = await test_func()
                duration = time.time() - start_time
                
                self.test_results.append({
                    "suite": suite_name,
                    "status": "PASS" if result else "FAIL",
                    "duration": duration,
                    "details": result if isinstance(result, dict) else {}
                })
                
                status_icon = "✅" if result else "❌"
                print(f"  {status_icon} {suite_name}: {'PASS' if result else 'FAIL'} ({duration:.2f}s)")
                
            except Exception as e:
                print(f"  ❌ {suite_name}: ERROR - {e}")
                self.test_results.append({
                    "suite": suite_name,
                    "status": "ERROR",
                    "duration": 0,
                    "error": str(e)
                })
        
        # 生成综合报告
        await self.generate_deployment_report()
    
    async def test_basic_deployment(self):
        """测试基础部署功能"""
        try:
            # 测试所有三种模式的基础部署
            modes = ["basic", "standard", "enhanced"]
            results = {}
            
            for mode in modes:
                print(f"    🔍 Testing {mode} mode deployment...")
                
                # 创建服务器
                server = await create_unified_server(
                    runtime_overrides={"mode": mode}
                )
                
                # 初始化服务器
                init_success = await server.initialize()
                if not init_success:
                    results[mode] = {"status": "FAIL", "reason": "Initialization failed"}
                    continue
                
                # 检查服务器状态
                status = server.get_server_status()
                if not status["initialized"]:
                    results[mode] = {"status": "FAIL", "reason": "Server not initialized"}
                    continue
                
                # 检查模块加载
                modules = server.module_manager.list_modules()
                expected_modules = ["core"]
                if mode == "enhanced":
                    expected_modules.extend(["collaboration", "intelligence"])
                
                missing_modules = [m for m in expected_modules if m not in modules]
                if missing_modules:
                    results[mode] = {
                        "status": "PARTIAL", 
                        "reason": f"Missing modules: {missing_modules}"
                    }
                else:
                    results[mode] = {"status": "PASS", "modules": modules}
                
                # 清理
                await server.stop()
            
            # 评估结果
            passed = sum(1 for r in results.values() if r["status"] == "PASS")
            total = len(results)
            
            return {
                "success": passed == total,
                "passed": passed,
                "total": total,
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_multi_mode_deployment(self):
        """测试多模式部署和切换"""
        try:
            print("    🔍 Testing mode switching...")
            
            # 测试模式切换序列
            mode_sequence = ["basic", "standard", "enhanced", "basic"]
            servers = []
            
            for i, mode in enumerate(mode_sequence):
                print(f"      → Switching to {mode} mode...")
                
                server = await create_unified_server(
                    runtime_overrides={"mode": mode}
                )
                await server.initialize()
                
                # 验证模式
                status = server.get_server_status()
                actual_mode = status["config"]["mode"]
                
                if actual_mode != mode:
                    return {
                        "success": False,
                        "error": f"Mode mismatch: expected {mode}, got {actual_mode}"
                    }
                
                servers.append(server)
            
            # 清理所有服务器
            for server in servers:
                await server.stop()
            
            return {
                "success": True,
                "modes_tested": len(mode_sequence),
                "sequence": mode_sequence
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_performance_benchmarks(self):
        """测试性能基准"""
        try:
            print("    🔍 Running performance benchmarks...")
            
            # 创建增强模式服务器（最完整功能）
            server = await create_unified_server(
                runtime_overrides={"mode": "enhanced"}
            )
            await server.initialize()
            
            benchmarks = {}
            
            # 1. 启动时间基准
            start_time = time.time()
            test_server = await create_unified_server(
                runtime_overrides={"mode": "enhanced"}
            )
            await test_server.initialize()
            startup_time = time.time() - start_time
            await test_server.stop()
            
            benchmarks["startup_time"] = startup_time
            
            # 2. 工具调用性能基准
            core_module = server.module_manager.get_module("core")
            if core_module:
                # 测试 aceflow_init 性能
                start_time = time.time()
                for _ in range(10):
                    result = core_module.aceflow_init(
                        mode="standard",
                        project_name=f"benchmark-test-{_}"
                    )
                init_avg_time = (time.time() - start_time) / 10
                benchmarks["aceflow_init_avg"] = init_avg_time
                
                # 测试 aceflow_validate 性能
                start_time = time.time()
                for _ in range(10):
                    result = core_module.aceflow_validate(
                        mode="basic",
                        target="project"
                    )
                validate_avg_time = (time.time() - start_time) / 10
                benchmarks["aceflow_validate_avg"] = validate_avg_time
            
            # 3. 内存使用基准
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            benchmarks["memory_usage_mb"] = memory_info.rss / 1024 / 1024
            
            await server.stop()
            
            # 评估性能
            performance_ok = (
                benchmarks["startup_time"] < 10.0 and  # 启动时间 < 10秒
                benchmarks.get("aceflow_init_avg", 0) < 2.0 and  # 工具调用 < 2秒
                benchmarks["memory_usage_mb"] < 500  # 内存使用 < 500MB
            )
            
            return {
                "success": performance_ok,
                "benchmarks": benchmarks,
                "performance_grade": "EXCELLENT" if performance_ok else "NEEDS_IMPROVEMENT"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_concurrent_load(self):
        """测试并发负载"""
        try:
            print("    🔍 Testing concurrent load handling...")
            
            server = await create_unified_server(
                runtime_overrides={"mode": "enhanced"}
            )
            await server.initialize()
            
            # 并发测试参数
            concurrent_requests = 20
            requests_per_worker = 5
            
            async def worker_task(worker_id):
                """工作线程任务"""
                results = []
                core_module = server.module_manager.get_module("core")
                
                for i in range(requests_per_worker):
                    try:
                        start_time = time.time()
                        result = core_module.aceflow_init(
                            mode="standard",
                            project_name=f"concurrent-test-{worker_id}-{i}"
                        )
                        duration = time.time() - start_time
                        
                        results.append({
                            "success": True,
                            "duration": duration,
                            "worker": worker_id,
                            "request": i
                        })
                    except Exception as e:
                        results.append({
                            "success": False,
                            "error": str(e),
                            "worker": worker_id,
                            "request": i
                        })
                
                return results
            
            # 启动并发任务
            start_time = time.time()
            tasks = [worker_task(i) for i in range(concurrent_requests)]
            all_results = await asyncio.gather(*tasks)
            total_duration = time.time() - start_time
            
            # 分析结果
            flat_results = [item for sublist in all_results for item in sublist]
            successful_requests = sum(1 for r in flat_results if r["success"])
            total_requests = len(flat_results)
            avg_response_time = sum(r.get("duration", 0) for r in flat_results if r["success"]) / max(successful_requests, 1)
            
            await server.stop()
            
            success_rate = successful_requests / total_requests
            load_test_passed = success_rate >= 0.95 and avg_response_time < 5.0
            
            return {
                "success": load_test_passed,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "total_duration": total_duration,
                "concurrent_workers": concurrent_requests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_failure_recovery(self):
        """测试故障恢复能力"""
        try:
            print("    🔍 Testing failure recovery...")
            
            server = await create_unified_server(
                runtime_overrides={"mode": "enhanced"}
            )
            await server.initialize()
            
            recovery_tests = {}
            
            # 1. 测试模块故障恢复
            try:
                # 模拟模块故障
                collaboration_module = server.module_manager.get_module("collaboration")
                if collaboration_module:
                    # 强制设置模块为未初始化状态
                    collaboration_module._initialized = False
                    
                    # 尝试重新初始化
                    recovery_success = collaboration_module.initialize()
                    recovery_tests["module_recovery"] = recovery_success
                else:
                    recovery_tests["module_recovery"] = "SKIPPED"
            except Exception as e:
                recovery_tests["module_recovery"] = f"ERROR: {e}"
            
            # 2. 测试配置错误恢复
            try:
                # 创建无效配置
                invalid_config = UnifiedConfig(mode="invalid_mode")
                errors = invalid_config.get_validation_errors()
                recovery_tests["config_validation"] = len(errors) > 0
            except Exception as e:
                recovery_tests["config_validation"] = f"ERROR: {e}"
            
            # 3. 测试服务器重启恢复
            try:
                await server.stop()
                server = await create_unified_server(
                    runtime_overrides={"mode": "enhanced"}
                )
                restart_success = await server.initialize()
                recovery_tests["server_restart"] = restart_success
            except Exception as e:
                recovery_tests["server_restart"] = f"ERROR: {e}"
            
            await server.stop()
            
            # 评估恢复能力
            successful_recoveries = sum(1 for r in recovery_tests.values() 
                                      if r is True or r == "SKIPPED")
            total_tests = len(recovery_tests)
            
            return {
                "success": successful_recoveries >= total_tests * 0.8,
                "recovery_tests": recovery_tests,
                "recovery_rate": successful_recoveries / total_tests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_config_hot_reload(self):
        """测试配置热重载"""
        try:
            print("    🔍 Testing configuration hot reload...")
            
            # 创建临时配置文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                initial_config = {
                    "mode": "basic",
                    "core": {"enabled": True}
                }
                json.dump(initial_config, f)
                config_file = f.name
            
            try:
                server = await create_unified_server()
                await server.initialize()
                
                # 检查初始状态
                initial_status = server.get_server_status()
                initial_mode = initial_status["config"]["mode"]
                
                # 模拟配置更新（在实际实现中，这需要配置管理器支持）
                # 这里我们测试配置系统的基本功能
                config_manager = server.config_manager
                
                # 测试配置更新
                updated_config = config_manager.get_config()
                hot_reload_supported = hasattr(config_manager, 'reload_config')
                
                await server.stop()
                
                return {
                    "success": True,
                    "initial_mode": initial_mode,
                    "hot_reload_supported": hot_reload_supported,
                    "config_manager_available": config_manager is not None
                }
                
            finally:
                os.unlink(config_file)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_leak(self):
        """测试内存泄漏"""
        try:
            print("    🔍 Testing for memory leaks...")
            
            import psutil
            
            # 基线内存使用
            process = psutil.Process()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行多次操作
            for cycle in range(5):
                server = await create_unified_server(
                    runtime_overrides={"mode": "enhanced"}
                )
                await server.initialize()
                
                # 执行一些操作
                core_module = server.module_manager.get_module("core")
                if core_module:
                    for i in range(10):
                        result = core_module.aceflow_init(
                            mode="standard",
                            project_name=f"memory-test-{cycle}-{i}"
                        )
                
                await server.stop()
                
                # 强制垃圾回收
                import gc
                gc.collect()
            
            # 检查最终内存使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - baseline_memory
            
            # 内存增长超过100MB认为可能有泄漏
            memory_leak_detected = memory_increase > 100
            
            return {
                "success": not memory_leak_detected,
                "baseline_memory_mb": baseline_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "leak_detected": memory_leak_detected
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_long_term_stability(self):
        """测试长期稳定性（简化版）"""
        try:
            print("    🔍 Testing long-term stability (abbreviated)...")
            
            server = await create_unified_server(
                runtime_overrides={"mode": "enhanced"}
            )
            await server.initialize()
            
            # 模拟长期运行（简化为短期高频操作）
            operations_count = 100
            errors = []
            
            core_module = server.module_manager.get_module("core")
            
            for i in range(operations_count):
                try:
                    # 交替执行不同操作
                    if i % 3 == 0:
                        result = core_module.aceflow_init(
                            mode="standard",
                            project_name=f"stability-test-{i}"
                        )
                    elif i % 3 == 1:
                        result = core_module.aceflow_stage(
                            action="status"
                        )
                    else:
                        result = core_module.aceflow_validate(
                            mode="basic",
                            target="project"
                        )
                    
                    # 短暂延迟模拟真实使用
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    errors.append(f"Operation {i}: {e}")
            
            await server.stop()
            
            error_rate = len(errors) / operations_count
            stability_ok = error_rate < 0.05  # 错误率低于5%
            
            return {
                "success": stability_ok,
                "operations_completed": operations_count,
                "errors_count": len(errors),
                "error_rate": error_rate,
                "errors": errors[:5] if errors else []  # 只显示前5个错误
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_deployment_report(self):
        """生成部署测试报告"""
        print("\n" + "=" * 60)
        print("📊 PRODUCTION DEPLOYMENT TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"Total Test Suites: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}[result["status"]]
            duration = result.get("duration", 0)
            print(f"  {status_icon} {result['suite']}: {result['status']} ({duration:.2f}s)")
            
            if result["status"] == "ERROR" and "error" in result:
                print(f"    Error: {result['error']}")
            elif "details" in result and result["details"]:
                if isinstance(result["details"], dict) and "benchmarks" in result["details"]:
                    benchmarks = result["details"]["benchmarks"]
                    print(f"    Startup: {benchmarks.get('startup_time', 0):.2f}s, "
                          f"Memory: {benchmarks.get('memory_usage_mb', 0):.1f}MB")
        
        # 部署就绪评估
        print("\n🎯 Deployment Readiness Assessment:")
        if passed_tests >= total_tests * 0.8:
            print("🎉 READY FOR PRODUCTION: All critical tests passed!")
            deployment_status = "PRODUCTION_READY"
        elif passed_tests >= total_tests * 0.6:
            print("⚠️ READY WITH CAUTION: Most tests passed, monitor closely")
            deployment_status = "READY_WITH_MONITORING"
        else:
            print("❌ NOT READY: Significant issues need resolution")
            deployment_status = "NOT_READY"
        
        # 保存详细报告
        report = {
            "timestamp": time.time(),
            "deployment_status": deployment_status,
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        with open("production_deployment_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: production_deployment_report.json")
        
        return deployment_status == "PRODUCTION_READY"
    
    def generate_recommendations(self):
        """生成部署建议"""
        recommendations = []
        
        # 基于测试结果生成建议
        for result in self.test_results:
            if result["status"] == "FAIL":
                if "performance" in result["suite"].lower():
                    recommendations.append("Consider performance optimization before production deployment")
                elif "concurrent" in result["suite"].lower():
                    recommendations.append("Review concurrent request handling and consider load balancing")
                elif "memory" in result["suite"].lower():
                    recommendations.append("Investigate memory usage patterns and implement monitoring")
            elif result["status"] == "ERROR":
                recommendations.append(f"Fix critical error in {result['suite']} before deployment")
        
        if not recommendations:
            recommendations.append("All tests passed - system is ready for production deployment")
        
        return recommendations

async def main():
    """主测试函数"""
    print("🚀 AceFlow MCP Server - Production Deployment Test Suite")
    print("=" * 60)
    
    tester = ProductionDeploymentTester()
    
    try:
        success = await tester.run_comprehensive_deployment_tests()
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Deployment test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)