"""
Workflow Engine

Core orchestrator for AceFlow workflow execution.
Manages workflow initialization, execution, and transitions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings

from ..models import (
    WorkflowMode, Iteration, Stage, StageStatus,
    # v4.0 models
    WorkflowType, WorkItem, WorkItemStatus, Task
)
from .state import StateManager


class WorkflowEngine:
    """Core workflow execution engine"""

    def __init__(self, project_id: str = "default"):
        self.project_id = project_id
        self.state_manager = StateManager(project_id)

        # v3.0 mode implementations (deprecated)
        self._mode_implementations = {}  # Will be registered by mode classes

        # v4.0 workflow registry (for 6 workflow types)
        self._workflow_registry = {}  # {WorkflowType: workflow_class_instance}

    def initialize(self, mode: str, metadata: Optional[Dict[str, Any]] = None,
                  iteration_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize a new workflow iteration (v3.0 - DEPRECATED)

        .. deprecated:: 4.0
           Use :func:`start_work_item` instead for v4.0 workflows.

        Args:
            mode: Workflow mode ('minimal', 'standard', 'complete', 'smart')
            metadata: Optional metadata for the iteration
            iteration_id: Optional custom iteration ID

        Returns:
            Dict containing iteration information
        """
        warnings.warn(
            "initialize() is deprecated in v4.0. Use start_work_item() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Convert string to enum
        workflow_mode = WorkflowMode(mode.lower())

        # Get mode implementation
        mode_impl = self._get_mode_implementation(workflow_mode)
        if not mode_impl:
            raise ValueError(f"No implementation found for mode: {mode}")

        # Initialize iteration with empty stages
        iteration = self.state_manager.initialize_iteration(workflow_mode, metadata, iteration_id)

        # Let mode implementation create its stages
        stages = mode_impl.create_stages()
        iteration.stages = stages

        # Mark first stage as in progress
        if stages:
            stages[0].status = StageStatus.IN_PROGRESS
            stages[0].start_time = datetime.now()

        # Save updated iteration
        self.state_manager._save_state()

        return {
            'iteration_id': iteration.iteration_id,
            'mode': iteration.mode.value,
            'total_stages': len(iteration.stages),
            'stages': [
                {
                    'stage_id': stage.stage_id,
                    'name': stage.name,
                    'description': stage.description
                }
                for stage in iteration.stages
            ],
            'current_stage': iteration.current_stage.to_dict() if iteration.current_stage else None,
            'status': 'initialized'
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current workflow status

        Returns:
            Dict containing workflow status information
        """
        return self.state_manager.get_state_summary()

    def advance(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Advance to next stage

        Args:
            metadata: Optional metadata for the transition

        Returns:
            Dict containing transition result
        """
        success = self.state_manager.advance_stage(metadata)

        if success:
            current_stage = self.state_manager.get_current_stage()
            return {
                'success': True,
                'message': f'Advanced to stage: {current_stage.name}' if current_stage else 'Advanced',
                'current_stage': current_stage.to_dict() if current_stage else None
            }
        else:
            return {
                'success': False,
                'message': 'Cannot advance: already at final stage or no active iteration'
            }

    def update_progress(self, progress: float, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update current stage progress

        Args:
            progress: Progress value (0.0 to 1.0)
            metadata: Optional metadata

        Returns:
            Dict containing update result
        """
        self.state_manager.update_stage_progress(progress, metadata)

        return {
            'success': True,
            'message': f'Progress updated to {progress:.1%}',
            'current_stage': self.state_manager.get_current_stage().to_dict() if self.state_manager.get_current_stage() else None
        }

    def rollback(self) -> Dict[str, Any]:
        """
        Rollback to previous stage

        Returns:
            Dict containing rollback result
        """
        success = self.state_manager.rollback_stage()

        if success:
            current_stage = self.state_manager.get_current_stage()
            return {
                'success': True,
                'message': f'Rolled back to stage: {current_stage.name}' if current_stage else 'Rolled back',
                'current_stage': current_stage.to_dict() if current_stage else None
            }
        else:
            return {
                'success': False,
                'message': 'Cannot rollback: already at first stage or no active iteration'
            }

    def validate(self) -> Dict[str, Any]:
        """
        Validate current workflow state

        Returns:
            Dict containing validation results
        """
        return self.state_manager.validate_state()

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transition history

        Args:
            limit: Maximum number of transitions to return

        Returns:
            List of transition records
        """
        return self.state_manager.get_transition_history(limit)

    def register_mode_implementation(self, mode: WorkflowMode, implementation):
        """
        Register a mode implementation

        Args:
            mode: WorkflowMode enum
            implementation: Mode implementation instance
        """
        self._mode_implementations[mode] = implementation

    def _get_mode_implementation(self, mode: WorkflowMode):
        """Get mode implementation"""
        return self._mode_implementations.get(mode)

    # ==================== v4.0 API Methods ====================

    def start_work_item(
        self,
        type: WorkflowType,
        title: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and start a new work item (v4.0)

        Args:
            type: Workflow type (feature, bugfix, refactor, review, documentation, performance)
            title: Work item title
            description: Detailed description
            metadata: Optional metadata

        Returns:
            Dict containing work item information and current stage details
        """
        # Get workflow implementation for this type
        workflow_impl = self._get_workflow_implementation(type)
        if not workflow_impl:
            raise ValueError(f"No workflow implementation found for type: {type.value}")

        # Create work item
        work_item = self.state_manager.create_work_item(
            type=type,
            title=title,
            description=description,
            metadata=metadata
        )

        # Initialize stages from workflow implementation
        stages = workflow_impl.get_stages()
        work_item.stages = stages

        # Mark first stage as in progress
        if stages:
            stages[0].status = StageStatus.IN_PROGRESS
            stages[0].start_time = datetime.now()
            work_item.current_stage_id = stages[0].stage_id

        # Update work item status
        work_item.status = WorkItemStatus.IN_PROGRESS
        self.state_manager._save_work_item(work_item)

        return {
            'success': True,
            'work_item_id': work_item.work_item_id,
            'type': work_item.type.value,
            'title': work_item.title,
            'status': work_item.status.value,
            'total_stages': len(work_item.stages),
            'stages': [
                {
                    'stage_id': stage.stage_id,
                    'name': stage.name,
                    'description': stage.description
                }
                for stage in work_item.stages
            ],
            'current_stage': work_item.current_stage.to_dict() if work_item.current_stage else None,
            'supports_subtasks': work_item.supports_subtasks(),
            'message': f'Work item created: {work_item.title}'
        }

    def get_current_work_item(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active work item (v4.0)

        Returns:
            Dict containing work item details or None if no active work item
        """
        work_item = self.state_manager.get_active_work_item()
        if not work_item:
            return None

        return {
            'work_item_id': work_item.work_item_id,
            'type': work_item.type.value,
            'title': work_item.title,
            'description': work_item.description,
            'status': work_item.status.value,
            'current_stage': work_item.current_stage.to_dict() if work_item.current_stage else None,
            'overall_progress': work_item.overall_progress,
            'task_progress': work_item.task_progress,
            'total_stages': len(work_item.stages),
            'total_tasks': len(work_item.tasks),
            'created_at': work_item.created_at.isoformat(),
            'updated_at': work_item.updated_at.isoformat()
        }

    def list_all_work_items(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all work items (v4.0)

        Args:
            status: Optional status filter (pending/in_progress/completed/cancelled/blocked)

        Returns:
            List of work item summaries
        """
        work_items = self.state_manager.list_work_items(status)

        return [
            {
                'work_item_id': item.work_item_id,
                'type': item.type.value,
                'title': item.title,
                'status': item.status.value,
                'overall_progress': item.overall_progress,
                'current_stage_id': item.current_stage_id,
                'total_stages': len(item.stages),
                'total_tasks': len(item.tasks),
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat()
            }
            for item in work_items
        ]

    def register_workflow_implementation(self, type: WorkflowType, implementation):
        """
        Register a workflow implementation (v4.0)

        Args:
            type: WorkflowType enum (feature, bugfix, etc.)
            implementation: Workflow implementation instance with get_stages() method
        """
        self._workflow_registry[type] = implementation

    def _get_workflow_implementation(self, type: WorkflowType):
        """Get workflow implementation for a specific type (v4.0)"""
        return self._workflow_registry.get(type)

