#!/usr/bin/env python3
"""
MCP Server Stdio 适配器 - 基于标准MCP SDK
将MCP协议请求转换为AceFlow工具调用，实现零开销适配
支持智能工作目录检测，确保MCP和CLI模式下的一致性
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import AceFlowTools
from .mcp_output_adapter import MCPOutputAdapter
from .tool_prompts import AceFlowToolPrompts
from .prompt_generator import AceFlowPromptGenerator
from .workflow.mcp.tools import WorkflowMCPTools
from pathlib import Path

# 设置日志到stderr，避免干扰stdio通信
logging.basicConfig(
    level=logging.WARNING,
    format='[MCP DEBUG] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


class MCPStdioServer:
    """MCP Server Stdio 适配器类"""
    
    def __init__(self):
        self.name = 'AceFlow'
        self.version = '1.0.4'
        self.debug = os.getenv('MCP_DEBUG', 'false').lower() == 'true'
        
        # 设置调试日志级别
        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        # 初始化执行上下文
        self.execution_context = self.get_execution_context()
        
        # 调试信息输出
        self.log(f"🎯 检测到执行模式: {self.execution_context['mode']}")
        self.log(f"📍 原始工作目录: {self.execution_context['originalCwd']}")
        self.log(f"📁 目标工作目录: {self.execution_context['workingDirectory']}")
        
        # 如果需要切换工作目录
        if self.execution_context['workingDirectory'] != self.execution_context['originalCwd']:
            self.log(f"🔄 切换工作目录: {self.execution_context['originalCwd']} -> {self.execution_context['workingDirectory']}")
            try:
                os.chdir(self.execution_context['workingDirectory'])
                self.log("✅ 工作目录切换成功")
            except Exception as error:
                self.log(f"❌ 工作目录切换失败: {error}")
                self.log(f"🔄 继续使用原始目录: {self.execution_context['originalCwd']}")
        
        # 基本调试信息
        self.log(f"📂 最终工作目录: {os.getcwd()}")
        
        # 创建输出适配器和工具实例
        self.output_adapter = MCPOutputAdapter()
        # 传递正确的工作目录给工具实例
        self.tools_instance = AceFlowTools(working_directory=self.execution_context['workingDirectory'])
        self.prompt_generator = AceFlowPromptGenerator()

        # 创建工作流 MCP 工具实例
        self.workflow_tools = WorkflowMCPTools(working_directory=Path(self.execution_context['workingDirectory']))
        
        # 创建MCP服务器实例
        self.server = Server(self.name)
        
        # 设置处理程序
        self.setup_handlers()
    
    def log(self, message: str):
        """调试日志 - 输出到stderr，不影响MCP协议"""
        if self.debug:
            logger.debug(message)
    
    def get_execution_context(self) -> Dict[str, str]:
        """智能检测执行上下文和工作目录"""
        args = sys.argv
        command = args[2] if len(args) > 2 else ''
        is_mcp_mode = command == 'mcp-server' or 'mcp' in ' '.join(args)
        
        # 获取真实的客户端工作目录
        # 优先级: 命令行传递 > MCP客户端环境变量 > 项目检测 > 当前目录
        client_working_dir = (
            self._get_client_directory_from_args() or
            os.environ.get('MCP_CWD') or           # MCP协议标准环境变量
            os.environ.get('CLIENT_CWD') or        # 客户端工作目录
            os.environ.get('VSCODE_CWD') or        # VS Code工作目录
            os.environ.get('CURSOR_CWD') or        # Cursor编辑器工作目录
            os.environ.get('PWD') or               # Unix风格当前目录
            os.environ.get('INIT_CWD') or          # npm/npx设置的原始目录
            os.environ.get('PROJECT_ROOT') or      # 项目根目录
            self._detect_client_directory() or     # 智能检测
            self._find_project_root() or           # 向上查找项目根目录
            os.getcwd()                           # 最后的后备选项
        )
        
        # 验证目录的有效性
        if not os.path.exists(client_working_dir):
            self.log(f"⚠️ 检测到的工作目录不存在: {client_working_dir}")
            client_working_dir = os.getcwd()
        
        return {
            'mode': 'MCP' if is_mcp_mode else 'CLI',
            'workingDirectory': client_working_dir,
            'originalCwd': os.getcwd()
        }
    
    def _get_client_directory_from_args(self) -> Optional[str]:
        """从命令行参数中获取客户端工作目录"""
        args = sys.argv
        for i, arg in enumerate(args):
            if arg in ['--cwd', '--working-directory'] and i + 1 < len(args):
                return args[i + 1]
            if arg.startswith('--cwd='):
                return arg.split('=', 1)[1]
            if arg.startswith('--working-directory='):
                return arg.split('=', 1)[1]
        return None
    
    def _find_project_root(self) -> Optional[str]:
        """向上查找项目根目录"""
        current = os.getcwd()
        path = os.path.abspath(current)
        
        # 避免在IDE安装目录中查找
        if any(pattern in path for pattern in ['Microsoft VS Code', 'Code.exe', 'vscode', 'cursor']):
            return None
            
        project_indicators = [
            '.git', '.hg', '.svn',          # 版本控制
            'package.json', 'pyproject.toml', 'requirements.txt',  # 配置文件
            'Cargo.toml', 'pom.xml', 'build.gradle',              # 其他语言
            'tsconfig.json', 'webpack.config.js',                 # 前端
            'Gemfile', 'composer.json',                           # Ruby, PHP
            'README.md', 'README.rst', 'README.txt'               # 文档
        ]
        
        # 最多向上查找5层
        for _ in range(5):
            for indicator in project_indicators:
                if os.path.exists(os.path.join(path, indicator)):
                    self.log(f"🎯 在 {path} 找到项目指示器: {indicator}")
                    return path
                    
            parent = os.path.dirname(path)
            if parent == path:  # 到达根目录
                break
            path = parent
            
        return None
    
    def _detect_client_directory(self) -> Optional[str]:
        """尝试检测客户端的真实工作目录"""
        # 检查父进程信息
        try:
            import psutil
            current_process = psutil.Process()
            parent_process = current_process.parent()
            
            if parent_process:
                # 如果父进程是VSCode、Cursor或其他编辑器
                parent_name = parent_process.name().lower()
                if any(editor in parent_name for editor in ['code', 'cursor', 'vscode', 'codebuddy']):
                    # 尝试从父进程的工作目录获取
                    return parent_process.cwd()
        except ImportError:
            # psutil不可用时的fallback
            self.log("psutil not available, using environment variables only")
        except Exception as e:
            self.log(f"Error detecting client directory: {e}")
        
        # 检查环境变量中的项目相关目录
        for env_var in ['VSCODE_CWD', 'PROJECT_CWD', 'WORKSPACE_FOLDER']:
            if env_var in os.environ:
                return os.environ[env_var]
        
        return None
    
    def setup_handlers(self):
        """设置MCP工具处理程序"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """列出可用工具"""
            self.log("📋 收到工具列表请求")

            tools = []

            # 1. 添加传统的 Contract-First 工具（4个）
            tool_definitions = AceFlowToolPrompts.get_tool_definitions()
            for tool_name, tool_def in tool_definitions.items():
                tools.append(Tool(
                    name=tool_def["name"],
                    description=tool_def["description"],
                    inputSchema=tool_def["inputSchema"]
                ))

            # 2. 添加 Workflow MCP 工具（21个）
            workflow_tool_schemas = self.workflow_tools.get_tool_schemas()
            for schema in workflow_tool_schemas:
                tools.append(Tool(
                    name=schema["name"],
                    description=schema["description"],
                    inputSchema=schema["inputSchema"]
                ))

            # 添加使用指导信息到日志
            self.log(f"✅ 返回 {len(tools)} 个工具（4个Contract + 21个Workflow）")
            for tool in tools:
                self.log(f"  - {tool.name}: {tool.description[:50]}...")

            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> Sequence[TextContent]:
            """执行工具调用"""
            self.log(f"🔧 调用工具: {name} 参数: {json.dumps(arguments or {})}")
            self.log(f"🗂️ 当前工作目录: {os.getcwd()}")
            
            try:
                # 设置超时控制
                result = await asyncio.wait_for(
                    self.execute_tool(name, arguments or {}),
                    timeout=30.0  # 30秒超时
                )
                
                self.log(f"✅ 工具执行完成: {name}")
                
                # 使用输出适配器转换为MCP响应格式
                mcp_response = self.output_adapter.convert_to_mcp_format(result)
                
                # 返回TextContent列表
                return [TextContent(
                    type="text",
                    text=mcp_response["content"][0]["text"]
                )]
                
            except asyncio.TimeoutError:
                error_msg = f"工具调用超时: {name}"
                self.log(f"⏰ {error_msg}")
                return [TextContent(
                    type="text",
                    text=self.output_adapter.create_error_response(error_msg)["content"][0]["text"]
                )]
                
            except Exception as error:
                error_msg = f"工具调用失败: {name} - {str(error)}"
                self.log(f"❌ {error_msg}")
                return [TextContent(
                    type="text",
                    text=self.output_adapter.handle_error(error)["content"][0]["text"]
                )]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行具体的工具调用"""
        try:
            # 1. 检查是否是 Contract-First 工具（传统工具）
            if tool_name in ["aceflow_init", "aceflow_stage", "aceflow_validate", "aceflow_template"]:
                if tool_name == "aceflow_init":
                    return self.tools_instance.aceflow_init(
                        mode=arguments["mode"],
                        project_name=arguments.get("project_name"),
                        directory=arguments.get("directory")
                    )
                elif tool_name == "aceflow_stage":
                    return self.tools_instance.aceflow_stage(
                        action=arguments["action"],
                        stage=arguments.get("stage"),
                        progress=arguments.get("progress")
                    )
                elif tool_name == "aceflow_validate":
                    return self.tools_instance.aceflow_validate(
                        mode=arguments.get("mode", "basic"),
                        fix=arguments.get("fix", False),
                        report=arguments.get("report", False)
                    )
                elif tool_name == "aceflow_template":
                    return self.tools_instance.aceflow_template(
                        action=arguments["action"],
                        template=arguments.get("template")
                    )

            # 2. 检查是否是 Workflow MCP 工具（新工具）
            elif tool_name in self.workflow_tools.tools:
                result = self.workflow_tools.execute_tool(tool_name, arguments)
                # 转换 MCPToolResult 为标准字典格式
                return {
                    "success": result.success,
                    "data": result.data,  # 修正: 使用 data 而不是 content
                    "error": result.error,
                    "metadata": result.metadata
                }

            else:
                raise ValueError(f"未知工具: {tool_name}")

        except Exception as e:
            logger.error(f"工具执行错误: {tool_name} - {str(e)}", exc_info=True)
            raise
    
    def setup_process_cleanup(self):
        """设置进程清理处理器"""
        def exit_handler(signum, frame):
            self.log(f"收到信号: {signum}")
            self.cleanup()
            sys.exit(0)
        
        # 捕获所有可能的退出信号
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, exit_handler)
        if hasattr(signal, 'SIGQUIT'):
            signal.signal(signal.SIGQUIT, exit_handler)
    
    def cleanup(self):
        """清理资源"""
        self.log("🔧 清理MCP Server资源")
    
    async def run(self):
        """启动MCP Server"""
        try:
            # 设置进程清理处理器
            self.setup_process_cleanup()
            
            self.log("🚀 启动MCP Server...")
            
            # 使用stdio传输
            async with stdio_server() as (read_stream, write_stream):
                self.log("✅ MCP Server 已启动，等待连接...")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
                
        except Exception as error:
            logger.error(f"❌ MCP Server 启动失败: {error}", exc_info=True)
            self.cleanup()
            raise


def main():
    """主函数"""
    server = MCPStdioServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        server.log("🛑 收到键盘中断，正在关闭...")
        server.cleanup()
    except Exception as e:
        logger.error(f"服务器运行错误: {e}", exc_info=True)
        server.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()