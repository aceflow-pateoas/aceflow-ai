"""Workflow Engine for AceFlow stage management."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum
import json
import os


class StageStatus(str, Enum):
    """Workflow stage status."""
    PENDING = "pending"           # 待开始
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    SKIPPED = "skipped"           # 已跳过
    BLOCKED = "blocked"           # 被阻塞


class WorkflowMode(str, Enum):
    """Workflow mode types."""
    STANDARD = "standard"
    COMPLETE = "complete"


class WorkflowEngine:
    """Manages workflow stages and transitions."""

    # Stage definitions for different modes
    STAGE_DEFINITIONS = {
        WorkflowMode.STANDARD: [
            "user_stories",
            "task_breakdown",
            "test_design",
            "implementation",
            "unit_test",
            "integration_test",
            "code_review"
        ],
        WorkflowMode.COMPLETE: [
            "requirement_analysis",
            "architecture_design",
            "user_stories",
            "task_breakdown",
            "test_design",
            "implementation",
            "unit_test",
            "integration_test",
            "performance_test",
            "code_review"
        ]
    }

    def __init__(self):
        """Initialize workflow engine."""
        self.current_dir = Path.cwd()
        self.state_file = self.current_dir / ".aceflow" / "current_state.json"

    def _load_state(self) -> Dict[str, Any]:
        """Load current state from file."""
        if not self.state_file.exists():
            # Return default state if file doesn't exist
            return self._get_default_state()

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Failed to load state file: {e}, using default state", file=os.sys.stderr)
            return self._get_default_state()

    def _save_state(self, state: Dict[str, Any]) -> bool:
        """Save state to file."""
        try:
            # Ensure .aceflow directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"[ERROR] Failed to save state file: {e}", file=os.sys.stderr)
            return False

    def _get_default_state(self) -> Dict[str, Any]:
        """Get default initial state."""
        return {
            "project": {
                "name": "untitled",
                "mode": WorkflowMode.STANDARD.value,
                "created_at": None,
                "version": "3.0"
            },
            "flow": {
                "current_stage": "user_stories",
                "stage_status": StageStatus.PENDING.value,
                "completed_stages": [],
                "progress_percentage": 0
            },
            "metadata": {
                "total_stages": 8,
                "last_updated": None
            }
        }

    def _get_workflow_mode(self, state: Dict[str, Any]) -> WorkflowMode:
        """Get workflow mode from state."""
        mode_str = state.get("project", {}).get("mode", "standard")
        try:
            return WorkflowMode(mode_str.lower())
        except ValueError:
            return WorkflowMode.STANDARD

    def _get_stages_for_mode(self, mode: WorkflowMode) -> List[str]:
        """Get stages for a specific mode."""
        return self.STAGE_DEFINITIONS.get(mode, self.STAGE_DEFINITIONS[WorkflowMode.STANDARD])

    def _calculate_overall_progress(self, completed_count: int, total_count: int, current_stage_progress: float = 0) -> float:
        """Calculate overall progress percentage.

        Args:
            completed_count: Number of completed stages
            total_count: Total number of stages
            current_stage_progress: Progress of current stage (0-100)

        Returns:
            Overall progress (0-100)
        """
        if total_count == 0:
            return 0

        # Each stage contributes (100 / total_count) percentage
        stage_weight = 100 / total_count

        # Completed stages contribute full weight
        completed_progress = completed_count * stage_weight

        # Current stage contributes partial weight
        current_progress = (current_stage_progress / 100) * stage_weight

        return round(completed_progress + current_progress, 2)

    def get_current_status(self) -> Dict[str, Any]:
        """Get current workflow status with detailed information.

        Returns:
            Dict with:
            - current_stage: Current stage info (name, status, description)
            - overall_progress: Overall project progress (0-100)
            - stage_progress: Current stage progress (0-100)
            - completed_stages: List of completed stage names
            - next_stage: Next stage name (if not at end)
            - total_stages: Total number of stages
            - remaining_stages: Number of remaining stages
        """
        state = self._load_state()
        mode = self._get_workflow_mode(state)
        all_stages = self._get_stages_for_mode(mode)

        flow = state.get("flow", {})
        current_stage_name = flow.get("current_stage", all_stages[0])
        stage_status = flow.get("stage_status", StageStatus.PENDING.value)
        completed_stages = flow.get("completed_stages", [])

        # Calculate progress
        current_stage_progress = flow.get("stage_progress", 0)  # 0-100
        overall_progress = self._calculate_overall_progress(
            len(completed_stages),
            len(all_stages),
            current_stage_progress
        )

        # Find next stage
        try:
            current_index = all_stages.index(current_stage_name)
            next_stage = all_stages[current_index + 1] if current_index < len(all_stages) - 1 else None
        except ValueError:
            next_stage = None

        return {
            "current_stage": {
                "name": current_stage_name,
                "status": stage_status,
                "progress": current_stage_progress,
                "index": all_stages.index(current_stage_name) + 1 if current_stage_name in all_stages else 0
            },
            "overall_progress": overall_progress,
            "completed_stages": completed_stages,
            "next_stage": next_stage,
            "total_stages": len(all_stages),
            "remaining_stages": len(all_stages) - len(completed_stages) - 1,  # -1 for current stage
            "workflow_mode": mode.value
        }

    def advance_to_next_stage(self) -> Dict[str, Any]:
        """Advance to the next workflow stage.

        Returns:
            Dict with:
            - success: Whether advancement was successful
            - previous_stage: Previous stage name
            - current_stage: New current stage info
            - message: Status message
        """
        state = self._load_state()
        mode = self._get_workflow_mode(state)
        all_stages = self._get_stages_for_mode(mode)

        flow = state.get("flow", {})
        current_stage_name = flow.get("current_stage", all_stages[0])
        completed_stages = flow.get("completed_stages", [])

        # Find current stage index
        try:
            current_index = all_stages.index(current_stage_name)
        except ValueError:
            return {
                "success": False,
                "error": f"Current stage '{current_stage_name}' not found in workflow",
                "message": "Invalid current stage"
            }

        # Check if already at the last stage
        if current_index >= len(all_stages) - 1:
            return {
                "success": False,
                "message": "Already at the final stage",
                "current_stage": {
                    "name": current_stage_name,
                    "status": StageStatus.COMPLETED.value,
                    "index": current_index + 1
                }
            }

        # Mark current stage as completed
        if current_stage_name not in completed_stages:
            completed_stages.append(current_stage_name)

        # Move to next stage
        next_stage_name = all_stages[current_index + 1]

        # Update state
        flow["current_stage"] = next_stage_name
        flow["stage_status"] = StageStatus.PENDING.value
        flow["stage_progress"] = 0
        flow["completed_stages"] = completed_stages
        flow["progress_percentage"] = self._calculate_overall_progress(
            len(completed_stages),
            len(all_stages),
            0
        )

        state["flow"] = flow

        # Save state
        self._save_state(state)

        # Calculate new overall progress
        overall_progress = self._calculate_overall_progress(
            len(completed_stages),
            len(all_stages),
            0
        )

        return {
            "success": True,
            "previous_stage": current_stage_name,
            "current_stage": {
                "name": next_stage_name,
                "status": StageStatus.PENDING.value,
                "progress": 0,
                "index": current_index + 2
            },
            "overall_progress": overall_progress,
            "completed_stages": completed_stages,
            "message": f"Advanced from '{current_stage_name}' to '{next_stage_name}'"
        }

    def update_stage_progress(self, progress: float) -> Dict[str, Any]:
        """Update current stage progress.

        Args:
            progress: Stage progress (0-100)

        Returns:
            Updated status dict
        """
        state = self._load_state()
        mode = self._get_workflow_mode(state)
        all_stages = self._get_stages_for_mode(mode)

        flow = state.get("flow", {})

        # Update stage progress
        flow["stage_progress"] = max(0, min(100, progress))  # Clamp to 0-100

        # Update stage status based on progress
        if progress > 0:
            flow["stage_status"] = StageStatus.IN_PROGRESS.value

        # Update overall progress
        completed_count = len(flow.get("completed_stages", []))
        flow["progress_percentage"] = self._calculate_overall_progress(
            completed_count,
            len(all_stages),
            progress
        )

        state["flow"] = flow
        self._save_state(state)

        return self.get_current_status()

    def list_all_stages(self) -> List[Dict[str, Any]]:
        """List all available stages with their status.

        Returns:
            List of stage dicts with name, status, index
        """
        state = self._load_state()
        mode = self._get_workflow_mode(state)
        all_stages = self._get_stages_for_mode(mode)

        flow = state.get("flow", {})
        current_stage = flow.get("current_stage", all_stages[0])
        completed_stages = flow.get("completed_stages", [])

        result = []
        for index, stage_name in enumerate(all_stages):
            if stage_name in completed_stages:
                status = StageStatus.COMPLETED.value
            elif stage_name == current_stage:
                status = flow.get("stage_status", StageStatus.PENDING.value)
            else:
                status = StageStatus.PENDING.value

            result.append({
                "name": stage_name,
                "index": index + 1,
                "status": status,
                "is_current": stage_name == current_stage
            })

        return result

    def reset_project(self) -> Dict[str, Any]:
        """Reset project to initial stage.

        Returns:
            Reset confirmation with new status
        """
        state = self._load_state()
        mode = self._get_workflow_mode(state)
        all_stages = self._get_stages_for_mode(mode)

        # Reset flow state
        state["flow"] = {
            "current_stage": all_stages[0],
            "stage_status": StageStatus.PENDING.value,
            "stage_progress": 0,
            "completed_stages": [],
            "progress_percentage": 0
        }

        self._save_state(state)

        return {
            "success": True,
            "message": "Project reset to initial stage",
            "current_stage": {
                "name": all_stages[0],
                "status": StageStatus.PENDING.value,
                "progress": 0
            },
            "overall_progress": 0,
            "completed_stages": []
        }

    def set_stage_status(self, status: StageStatus) -> Dict[str, Any]:
        """Set current stage status manually.

        Args:
            status: New stage status

        Returns:
            Updated status dict
        """
        state = self._load_state()
        flow = state.get("flow", {})

        flow["stage_status"] = status.value
        state["flow"] = flow

        self._save_state(state)

        return self.get_current_status()
