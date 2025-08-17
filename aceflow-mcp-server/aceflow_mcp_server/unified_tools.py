"""
统一工具接口 (Unified Tools Interface)
Unified Tools Interface
This module provides unified tool interfaces that combine basic and enhanced functionality
while maintaining backward compatibility.
"""
from typing import Dict, Any, Optional, List
import logging
import json
import os
from pathlib import Path
import datetime

logger = logging.getLogger(__name__)

class UnifiedToolsInterface:
    """
    统一工具接口
    
    提供统一的工具接口，合并基础和增强功能，
    支持智能路由和向后兼容性。
    """
    
    def __init__(self, config, module_manager, function_router, usage_monitor=None):
        """
        初始化统一工具接口
        
        Args:
            config: 统一配置对象
            module_manager: 模块管理器
            function_router: 功能路由器
            usage_monitor: 使用监控器（可选）
        """
        self.config = config
        self.module_manager = module_manager
        self.function_router = function_router
        self.usage_monitor = usage_monitor
        
        # 工具调用统计
        self._tool_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tool_distribution": {},
            "mode_distribution": {}
        }
        
        logger.info("Unified tools interface initialized successfully")
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None,
        # 新增统一配置参数
        collaboration_enabled: Optional[bool] = None,
        intelligence_enabled: Optional[bool] = None,
        # 向后兼容参数
        user_input: Optional[str] = None,
        auto_confirm: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        🚀 Initialize AceFlow project with unified configuration
        
        统一的项目初始化工具，合并基础和增强功能。
        
        Args:
            mode: 初始化模式 (minimal, standard, complete)
            project_name: 项目名称（可选）
            directory: 项目目录（可选）
            collaboration_enabled: 启用协作功能（可选）
            intelligence_enabled: 启用智能功能（可选）
            user_input: 用户输入（用于智能分析）
            auto_confirm: 自动确认（默认True）
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 初始化结果
        """
        start_time = datetime.datetime.now()
        
        try:
            # 记录工具调用
            self._record_tool_call("aceflow_init")
            
            # 构建参数字典
            parameters = {
                "mode": mode,
                "project_name": project_name,
                "directory": directory,
                "collaboration_enabled": collaboration_enabled,
                "intelligence_enabled": intelligence_enabled,
                "user_input": user_input,
                "auto_confirm": auto_confirm if auto_confirm is not None else True,
                **kwargs
            }
            
            # 构建执行上下文
            context = {
                "tool_name": "aceflow_init",
                "user_id": kwargs.get("user_id", "default"),
                "timestamp": start_time.isoformat()
            }
            
            # 生成执行计划
            execution_plan = self.function_router.plan_execution(
                "aceflow_init", 
                parameters, 
                context
            )
            
            # 记录执行模式
            self._record_execution_mode(execution_plan.mode.value)
            
            # 执行初始化
            result = self._execute_init_plan(execution_plan)
            
            # 记录成功调用
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self._record_successful_call(duration)
            
            # 记录使用监控
            if self.usage_monitor:
                self.usage_monitor.record_tool_usage(
                    tool_name="aceflow_init",
                    parameters=parameters,
                    execution_mode=execution_plan.mode.value,
                    duration_ms=duration * 1000,
                    success=True
                )
            
            logger.info(f"aceflow_init completed successfully in {duration:.3f}s, mode: {execution_plan.mode.value}")
            
            return {
                "success": True,
                "message": "Project initialized successfully",
                "result": result,
                "execution_plan": {
                    "mode": execution_plan.mode.value,
                    "primary_module": execution_plan.primary_module,
                    "enhancement_modules": execution_plan.enhancement_modules,
                    "confidence": execution_plan.confidence
                },
                "duration_ms": duration * 1000
            }
            
        except Exception as e:
            # 记录失败调用
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self._record_failed_call()
            
            # 记录使用监控
            if self.usage_monitor:
                self.usage_monitor.record_tool_usage(
                    tool_name="aceflow_init",
                    parameters=parameters if 'parameters' in locals() else {},
                    execution_mode="error",
                    duration_ms=duration * 1000,
                    success=False,
                    error=str(e)
                )
            
            logger.error(f"aceflow_init failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project",
                "duration_ms": duration * 1000
            }
    
    def _execute_init_plan(self, execution_plan) -> Dict[str, Any]:
        """
        执行初始化计划
        
        Args:
            execution_plan: 执行计划
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        result = {
            "project_initialized": False,
            "directory_created": False,
            "config_saved": False,
            "modules_initialized": [],
            "enhancements_applied": []
        }
        
        try:
            # 获取主模块
            primary_module = self.module_manager.get_module(execution_plan.primary_module)
            if not primary_module or not primary_module.is_available():
                raise RuntimeError(f"Primary module '{execution_plan.primary_module}' not available")
            
            # 执行核心初始化
            if execution_plan.primary_module == "core":
                core_result = self._execute_core_init(execution_plan.parameters)
                result.update(core_result)
                result["modules_initialized"].append("core")
            
            # 执行增强模块初始化
            for module_name in execution_plan.enhancement_modules:
                enhancement_module = self.module_manager.get_module(module_name)
                if enhancement_module and enhancement_module.is_available():
                    enhancement_result = self._execute_enhancement_init(
                        module_name, 
                        execution_plan.parameters
                    )
                    result["enhancements_applied"].append({
                        "module": module_name,
                        "result": enhancement_result
                    })
                    result["modules_initialized"].append(module_name)
                else:
                    logger.warning(f"Enhancement module '{module_name}' not available, skipping")
            
            # 保存运行时配置
            self._save_runtime_config(execution_plan)
            result["config_saved"] = True
            
            result["project_initialized"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute init plan: {e}")
            # 尝试降级执行
            if execution_plan.fallback_plan:
                logger.info("Attempting fallback execution")
                return self._execute_init_plan(execution_plan.fallback_plan)
            else:
                raise e
    
    def _execute_core_init(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行核心初始化
        
        Args:
            parameters: 初始化参数
            
        Returns:
            Dict[str, Any]: 核心初始化结果
        """
        result = {}
        
        # 获取核心模块
        core_module = self.module_manager.get_module("core")
        if not core_module:
            raise RuntimeError("Core module not available")
        
        # 调用核心模块的初始化方法
        if hasattr(core_module, 'aceflow_init'):
            core_result = core_module.aceflow_init(
                mode=parameters.get("mode", "standard"),
                project_name=parameters.get("project_name"),
                directory=parameters.get("directory"),
                **{k: v for k, v in parameters.items() if k not in ["mode", "project_name", "directory"]}
            )
            result.update(core_result)
        else:
            # 基础初始化逻辑
            result = self._basic_project_init(parameters)
        
        return result
    
    def _execute_enhancement_init(self, module_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行增强模块初始化
        
        Args:
            module_name: 模块名称
            parameters: 初始化参数
            
        Returns:
            Dict[str, Any]: 增强初始化结果
        """
        result = {"enhanced": False, "features": []}
        
        try:
            module = self.module_manager.get_module(module_name)
            if not module:
                return result
            
            if module_name == "collaboration":
                # 协作模块增强
                if parameters.get("user_input") and not parameters.get("auto_confirm", True):
                    result["features"].append("interactive_confirmation")
                    result["enhanced"] = True
                
                if parameters.get("collaboration_enabled", False):
                    result["features"].append("collaboration_tracking")
                    result["enhanced"] = True
            
            elif module_name == "intelligence":
                # 智能模块增强
                if parameters.get("user_input"):
                    # 执行意图分析
                    if hasattr(module, 'aceflow_intent_analyze'):
                        intent_result = module.aceflow_intent_analyze(
                            user_input=parameters["user_input"],
                            context={"tool": "aceflow_init"}
                        )
                        result["features"].append("intent_analysis")
                        result["intent_analysis"] = intent_result
                        result["enhanced"] = True
                
                if parameters.get("intelligence_enabled", False):
                    result["features"].append("smart_recommendations")
                    result["enhanced"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute {module_name} enhancement: {e}")
            return result
    
    def _basic_project_init(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        基础项目初始化
        
        Args:
            parameters: 初始化参数
            
        Returns:
            Dict[str, Any]: 初始化结果
        """
        result = {
            "project_name": parameters.get("project_name", "aceflow-project"),
            "mode": parameters.get("mode", "standard"),
            "directory": parameters.get("directory", os.getcwd()),
            "created_files": [],
            "created_directories": []
        }
        
        try:
            # 确定项目目录
            project_dir = Path(result["directory"])
            if parameters.get("project_name"):
                project_dir = project_dir / parameters["project_name"]
            
            # 创建项目目录
            project_dir.mkdir(parents=True, exist_ok=True)
            result["created_directories"].append(str(project_dir))
            
            # 创建 .aceflow 目录
            aceflow_dir = project_dir / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            result["created_directories"].append(str(aceflow_dir))
            
            # 创建基础配置文件
            config_file = aceflow_dir / "config.json"
            config_data = {
                "project": {
                    "name": result["project_name"],
                    "mode": result["mode"],
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "workflow": {
                    "current_stage": "initialization",
                    "stages": ["initialization", "planning", "implementation", "testing", "deployment"]
                },
                "features": {
                    "collaboration": parameters.get("collaboration_enabled", False),
                    "intelligence": parameters.get("intelligence_enabled", False)
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            result["created_files"].append(str(config_file))
            
            # 创建状态文件
            state_file = aceflow_dir / "current_state.json"
            state_data = {
                "project": config_data["project"],
                "flow": {
                    "current_stage": "initialization",
                    "progress_percentage": 10,
                    "completed_stages": [],
                    "next_stage": "planning"
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            result["created_files"].append(str(state_file))
            
            # 根据模式创建额外文件
            if result["mode"] in ["standard", "complete"]:
                # 创建 README.md
                readme_file = project_dir / "README.md"
                readme_content = f"""# {result['project_name']}

AceFlow project initialized with {result['mode']} mode.

## Project Structure

- `.aceflow/` - AceFlow configuration and state files
- `README.md` - This file

## Getting Started

Your project has been initialized successfully. You can now proceed with the next stages of development.

Created on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                result["created_files"].append(str(readme_file))
            
            if result["mode"] == "complete":
                # 创建更多结构文件
                for dir_name in ["src", "tests", "docs"]:
                    dir_path = project_dir / dir_name
                    dir_path.mkdir(exist_ok=True)
                    result["created_directories"].append(str(dir_path))
                    
                    # 创建 .gitkeep 文件
                    gitkeep_file = dir_path / ".gitkeep"
                    gitkeep_file.touch()
                    result["created_files"].append(str(gitkeep_file))
            
            result["directory_created"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Basic project initialization failed: {e}")
            raise e
    
    def _save_runtime_config(self, execution_plan):
        """
        保存运行时配置
        
        Args:
            execution_plan: 执行计划
        """
        try:
            # 确定配置保存位置
            project_dir = Path(execution_plan.parameters.get("directory", os.getcwd()))
            if execution_plan.parameters.get("project_name"):
                project_dir = project_dir / execution_plan.parameters["project_name"]
            
            aceflow_dir = project_dir / ".aceflow"
            aceflow_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存运行时配置
            runtime_config_file = aceflow_dir / "runtime_config.json"
            runtime_config = {
                "execution_plan": {
                    "mode": execution_plan.mode.value,
                    "primary_module": execution_plan.primary_module,
                    "enhancement_modules": execution_plan.enhancement_modules,
                    "confidence": execution_plan.confidence,
                    "created_at": execution_plan.created_at
                },
                "unified_config": {
                    "collaboration_enabled": getattr(self.config.collaboration, 'enabled', False),
                    "intelligence_enabled": getattr(self.config.intelligence, 'enabled', False),
                    "mode": getattr(self.config, 'mode', 'standard')
                },
                "tool_parameters": execution_plan.parameters,
                "saved_at": datetime.datetime.now().isoformat()
            }
            
            with open(runtime_config_file, 'w', encoding='utf-8') as f:
                json.dump(runtime_config, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Runtime config saved to {runtime_config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save runtime config: {e}")
    
    def _record_tool_call(self, tool_name: str):
        """记录工具调用"""
        self._tool_stats["total_calls"] += 1
        if tool_name not in self._tool_stats["tool_distribution"]:
            self._tool_stats["tool_distribution"][tool_name] = 0
        self._tool_stats["tool_distribution"][tool_name] += 1
    
    def _record_execution_mode(self, mode: str):
        """记录执行模式"""
        if mode not in self._tool_stats["mode_distribution"]:
            self._tool_stats["mode_distribution"][mode] = 0
        self._tool_stats["mode_distribution"][mode] += 1
    
    def _record_successful_call(self, duration: float):
        """记录成功调用"""
        self._tool_stats["successful_calls"] += 1
    
    def _record_failed_call(self):
        """记录失败调用"""
        self._tool_stats["failed_calls"] += 1
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        return self._tool_stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self._tool_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tool_distribution": {},
            "mode_distribution": {}
        }
        logger.info("Tool statistics reset")