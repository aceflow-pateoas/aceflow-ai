"""
AceFlow MCP Server Tools Module

This module provides the core tools for AceFlow MCP Server functionality.
"""

from typing import Dict, Any, Optional, List
import json
import os
import sys
from pathlib import Path
import shutil
import datetime

# Import core functionality
try:
    from .core import ProjectManager, WorkflowEngine, TemplateManager
except ImportError:
    # Fallback implementations for core functionality
    class ProjectManager:
        def __init__(self):
            pass
    
    class WorkflowEngine:
        def __init__(self):
            pass
    
    class TemplateManager:
        def __init__(self):
            pass

# Import existing AceFlow functionality
current_dir = Path(__file__).parent
aceflow_scripts_dir = current_dir.parent.parent / "aceflow" / "scripts"
sys.path.insert(0, str(aceflow_scripts_dir))

try:
    from utils.platform_compatibility import PlatformUtils, SafeFileOperations, EnhancedErrorHandler
except ImportError:
    # Fallback implementations if utils are not available
    class PlatformUtils:
        @staticmethod
        def get_os_type(): 
            return "unknown"
    
    class SafeFileOperations:
        @staticmethod
        def write_text_file(path, content, encoding="utf-8"):
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
    
    class EnhancedErrorHandler:
        @staticmethod
        def handle_file_error(error, context=""): 
            return str(error)


class AceFlowTools:
    """AceFlow MCP Tools collection."""
    
    def __init__(self):
        """Initialize tools with necessary dependencies."""
        self.platform_utils = PlatformUtils()
        self.file_ops = SafeFileOperations()
        self.error_handler = EnhancedErrorHandler()
        self.project_manager = ProjectManager()
        self.workflow_engine = WorkflowEngine()
        self.template_manager = TemplateManager()
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode.
        
        Args:
            mode: Workflow mode (minimal, standard, complete, smart)
            project_name: Optional project name
            directory: Optional target directory (defaults to current directory)
        
        Returns:
            Dict with success status, message, and project info
        """
        try:
            # Validate mode
            valid_modes = ["minimal", "standard", "complete", "smart"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                    "message": "Mode validation failed"
                }
            
            # Determine target directory
            if directory:
                target_dir = Path(directory).resolve()
            else:
                target_dir = Path.cwd()
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Set project name
            if not project_name:
                project_name = target_dir.name
            
            # Check if already initialized (unless forced)
            aceflow_dir = target_dir / ".aceflow"
            clinerules_file = target_dir / ".clinerules"
            
            if aceflow_dir.exists() or clinerules_file.exists():
                return {
                    "success": False,
                    "error": "Directory already contains AceFlow configuration",
                    "message": "Use --force flag to overwrite existing configuration"
                }
            
            # Initialize project structure
            result = self._initialize_project_structure(target_dir, project_name, mode)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"AceFlow project '{project_name}' initialized successfully",
                    "project_info": {
                        "name": project_name,
                        "directory": str(target_dir),
                        "mode": mode,
                        "aceflow_dir": str(aceflow_dir)
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Initialization failed due to unexpected error"
            }
    
    def aceflow_status(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """Get AceFlow project status.
        
        Args:
            directory: Optional project directory (defaults to current directory)
        
        Returns:
            Dict with project status information
        """
        try:
            if directory:
                target_dir = Path(directory).resolve()
            else:
                target_dir = Path.cwd()
            
            aceflow_dir = target_dir / ".aceflow"
            
            if not aceflow_dir.exists():
                return {
                    "success": False,
                    "error": "No AceFlow project found in current directory",
                    "message": "Use 'aceflow init' to initialize a project"
                }
            
            # Read project configuration
            config_file = aceflow_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Read project state
            state_file = aceflow_dir / "state" / "project_state.json"
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                state = {}
            
            return {
                "success": True,
                "project_info": {
                    "name": config.get("project_name", "Unknown"),
                    "mode": config.get("workflow_mode", "Unknown"),
                    "directory": str(target_dir),
                    "current_stage": state.get("current_stage", "Unknown"),
                    "progress": state.get("progress", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get project status"
            }
    
    def aceflow_stage(
        self,
        stage: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute or get information about AceFlow stages.
        
        Args:
            stage: Optional stage to execute (if None, returns current stage info)
            directory: Optional project directory
        
        Returns:
            Dict with stage execution or information result
        """
        try:
            if directory:
                target_dir = Path(directory).resolve()
            else:
                target_dir = Path.cwd()
            
            aceflow_dir = target_dir / ".aceflow"
            
            if not aceflow_dir.exists():
                return {
                    "success": False,
                    "error": "No AceFlow project found",
                    "message": "Use 'aceflow init' first"
                }
            
            if stage is None:
                # Return current stage information
                state_file = aceflow_dir / "state" / "project_state.json"
                if state_file.exists():
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    return {
                        "success": True,
                        "current_stage": state.get("current_stage", "Unknown"),
                        "progress": state.get("progress", 0),
                        "available_stages": ["S1", "S2", "S3", "S4", "S5"]
                    }
                else:
                    return {
                        "success": False,
                        "error": "Project state not found",
                        "message": "Project may be corrupted"
                    }
            else:
                # Execute specified stage
                return self._execute_stage(stage, target_dir)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Stage operation failed"
            }
    
    def _initialize_project_structure(
        self, 
        target_dir: Path, 
        project_name: str, 
        mode: str
    ) -> Dict[str, Any]:
        """Initialize the AceFlow project structure."""
        try:
            aceflow_dir = target_dir / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (aceflow_dir / "state").mkdir(exist_ok=True)
            (aceflow_dir / "templates").mkdir(exist_ok=True)
            (aceflow_dir / "scripts").mkdir(exist_ok=True)
            
            # Create project configuration
            config = {
                "project_name": project_name,
                "workflow_mode": mode,
                "created_at": datetime.datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            config_file = aceflow_dir / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Create initial project state
            state = {
                "current_stage": "S1",
                "progress": 0,
                "stages_completed": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            state_file = aceflow_dir / "state" / "project_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": "Project structure created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create project structure"
            }
    
    def _execute_stage(self, stage: str, target_dir: Path) -> Dict[str, Any]:
        """Execute a specific AceFlow stage."""
        try:
            valid_stages = ["S1", "S2", "S3", "S4", "S5"]
            if stage not in valid_stages:
                return {
                    "success": False,
                    "error": f"Invalid stage '{stage}'. Valid stages: {', '.join(valid_stages)}",
                    "message": "Stage validation failed"
                }
            
            # For now, just update the state to indicate stage execution
            state_file = target_dir / ".aceflow" / "state" / "project_state.json"
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                state = {}
            
            state["current_stage"] = stage
            state["last_updated"] = datetime.datetime.now().isoformat()
            
            if stage not in state.get("stages_completed", []):
                state.setdefault("stages_completed", []).append(stage)
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": f"Stage {stage} executed successfully",
                "stage": stage,
                "current_time": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage {stage}"
            }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their descriptions.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "aceflow_init",
                "description": "Initialize a new AceFlow project",
                "parameters": {
                    "mode": {
                        "type": "string",
                        "description": "Workflow mode (minimal, standard, complete, smart)",
                        "enum": ["minimal", "standard", "complete", "smart"]
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name (optional)"
                    },
                    "directory": {
                        "type": "string", 
                        "description": "Target directory (optional)"
                    }
                }
            },
            {
                "name": "aceflow_status",
                "description": "Get current AceFlow project status",
                "parameters": {
                    "directory": {
                        "type": "string",
                        "description": "Project directory (optional)"
                    }
                }
            },
            {
                "name": "aceflow_stage", 
                "description": "Execute or get information about AceFlow stages",
                "parameters": {
                    "stage": {
                        "type": "string",
                        "description": "Stage to execute (S1, S2, S3, S4, S5) or null for current info",
                        "enum": ["S1", "S2", "S3", "S4", "S5"]
                    },
                    "directory": {
                        "type": "string",
                        "description": "Project directory (optional)"
                    }
                }
            }
        ]


# Export the tools class for MCP server usage
def get_aceflow_tools() -> AceFlowTools:
    """Get an instance of AceFlowTools for MCP server."""
    return AceFlowTools()
