"""
构建钩子 - 在打包前自动同步模板文件
确保打包的MCP服务器包含最新的模板文件
"""

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess
import sys
from pathlib import Path


class CustomBuildHook(BuildHookInterface):
    """自定义构建钩子"""
    
    PLUGIN_NAME = "custom"
    
    def initialize(self, version, build_data):
        """构建初始化时执行"""
        print("AceFlow MCP Server build hook starting...")
        
        # 执行模板同步
        sync_script = Path(self.root) / "scripts" / "sync_templates.py"
        if sync_script.exists():
            try:
                print("Syncing template files...")
                result = subprocess.run([
                    sys.executable, str(sync_script), "--sync"
                ], capture_output=True, text=True, cwd=self.root)
                
                if result.returncode == 0:
                    print("Template sync successful")
                    if result.stdout:
                        print(result.stdout)
                else:
                    print("Template sync failed")
                    if result.stderr:
                        print(result.stderr)
                    # 不阻止构建，但发出警告
                    print("Warning: Continuing build, but templates may not be latest version")
            except Exception as e:
                print(f"Error executing template sync: {e}")
                print("Warning: Continuing build, but templates may not be latest version")
        else:
            print("Warning: Template sync script not found, skipping sync")