"""
PATEOAS (Prompt as Engine of AI State) 增强模块
为 AceFlow 提供状态连续性、智能记忆和自适应流程控制能力
"""

from .models import PATEOASState, MemoryFragment, NextAction, ReasoningStep
from .state_manager import StateContinuityManager
from .memory_system import ContextMemorySystem
from .flow_controller import AdaptiveFlowController
# 临时注释决策门导入，避免循环导入问题
# from .decision_gates import (
#     IntelligentDecisionGate, 
#     OptimizedDG1, 
#     OptimizedDG2, 
#     DecisionGateManager,
#     DecisionGateFactory,
#     DecisionGateResult,
#     DecisionGateEvaluation
# )
from .enhanced_engine import PATEOASEnhancedEngine

__version__ = "1.0.0"
__all__ = [
    "PATEOASState",
    "MemoryFragment", 
    "NextAction",
    "ReasoningStep",
    "StateContinuityManager",
    "ContextMemorySystem",
    "AdaptiveFlowController",
    "IntelligentDecisionGate",
    "OptimizedDG1",
    "OptimizedDG2", 
    "DecisionGateManager",
    "DecisionGateFactory",
    "DecisionGateResult",
    "DecisionGateEvaluation",
    "PATEOASEnhancedEngine"
]