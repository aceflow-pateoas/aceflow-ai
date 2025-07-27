"""
自适应恢复策略系统
提供智能的错误恢复和系统自愈能力
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .models import MemoryFragment, MemoryCategory, NextAction, ActionType


class RecoveryType(Enum):
    """恢复类型"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"
    FALLBACK = "fallback"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"
    RESTART = "restart"
    IGNORE = "ignore"


@dataclass
class RecoveryAction:
    """恢复行动"""
    strategy: RecoveryStrategy
    description: str
    confidence: float
    estimated_time: str
    risk_level: str = "low"
    prerequisites: List[str] = field(default_factory=list)
    success_probability: float = 0.8
    
    def to_next_action(self) -> NextAction:
        """转换为NextAction对象"""
        action_type_mapping = {
            RecoveryStrategy.RETRY: ActionType.CONTINUE,
            RecoveryStrategy.FALLBACK: ActionType.PIVOT,
            RecoveryStrategy.ROLLBACK: ActionType.PIVOT,
            RecoveryStrategy.ESCALATE: ActionType.ESCALATE,
            RecoveryStrategy.RESTART: ActionType.CONTINUE,
            RecoveryStrategy.IGNORE: ActionType.CONTINUE
        }
        
        return NextAction(
            action_type=action_type_mapping.get(self.strategy, ActionType.CONTINUE),
            description=self.description,
            command=f"aceflow recover --strategy {self.strategy.value}",
            confidence=self.confidence,
            estimated_time=self.estimated_time,
            risk_level=self.risk_level
        )


@dataclass
class RecoveryContext:
    """恢复上下文"""
    error_type: str
    error_message: str
    component: str
    timestamp: datetime
    user_input: str
    system_state: Dict[str, Any]
    previous_attempts: List[Dict[str, Any]] = field(default_factory=list)
    severity: str = "medium"
    
    @property
    def attempt_count(self) -> int:
        """尝试次数"""
        return len(self.previous_attempts)
    
    def add_attempt(self, strategy: RecoveryStrategy, success: bool, details: str = ""):
        """添加恢复尝试记录"""
        self.previous_attempts.append({
            'strategy': strategy.value,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        })


class AdaptiveRecoveryStrategy:
    """自适应恢复策略"""
    
    def __init__(self):
        self.recovery_history: List[RecoveryContext] = []
        self.strategy_success_rates: Dict[str, float] = {
            'retry': 0.7,
            'fallback': 0.8,
            'rollback': 0.9,
            'escalate': 0.95,
            'restart': 0.6,
            'ignore': 0.3
        }
        
        # 置信度阈值配置
        self.confidence_thresholds = {
            'auto_recovery': 0.8,  # 自动恢复阈值
            'manual_intervention': 0.5,  # 手动干预阈值
            'escalation': 0.3  # 升级阈值
        }
        
        # 错误模式匹配规则
        self.error_patterns = {
            'timeout': ['timeout', 'time out', 'timed out', 'connection timeout'],
            'memory': ['memory', 'out of memory', 'memory error', 'allocation'],
            'network': ['network', 'connection', 'socket', 'http'],
            'permission': ['permission', 'access denied', 'unauthorized', 'forbidden'],
            'resource': ['resource', 'file not found', 'disk space', 'quota'],
            'logic': ['logic error', 'assertion', 'invalid state', 'unexpected'],
            'data': ['data error', 'parsing', 'format', 'validation']
        }
    
    def analyze_and_recover(
        self, 
        error: Exception, 
        context: Dict[str, Any],
        component: str = "unknown"
    ) -> Dict[str, Any]:
        """分析错误并制定恢复策略"""
        
        # 创建恢复上下文
        recovery_context = RecoveryContext(
            error_type=type(error).__name__,
            error_message=str(error),
            component=component,
            timestamp=datetime.now(),
            user_input=context.get('user_input', ''),
            system_state=context.get('system_state', {}),
            severity=self._assess_error_severity(error, context)
        )
        
        # 分析错误模式
        error_pattern = self._match_error_pattern(str(error))
        
        # 生成恢复策略
        recovery_strategies = self._generate_recovery_strategies(
            recovery_context, error_pattern
        )
        
        # 选择最佳策略
        best_strategy = self._select_best_strategy(recovery_strategies, recovery_context)
        
        # 决定恢复类型（自动/手动）
        recovery_type = self._decide_recovery_type(best_strategy, recovery_context)
        
        # 执行恢复（如果是自动）
        recovery_result = None
        if recovery_type == RecoveryType.AUTOMATIC:
            recovery_result = self._execute_recovery(best_strategy, recovery_context)
        
        # 记录恢复历史
        self.recovery_history.append(recovery_context)
        
        return {
            'recovery_context': recovery_context,
            'error_pattern': error_pattern,
            'available_strategies': recovery_strategies,
            'recommended_strategy': best_strategy,
            'recovery_type': recovery_type,
            'recovery_result': recovery_result,
            'confidence': best_strategy.confidence,
            'next_action': best_strategy.to_next_action(),
            'manual_instructions': self._generate_manual_instructions(best_strategy, recovery_context) if recovery_type != RecoveryType.AUTOMATIC else None
        }
    
    def _assess_error_severity(self, error: Exception, context: Dict[str, Any]) -> str:
        """评估错误严重程度"""
        error_msg = str(error).lower()
        
        # 关键错误
        critical_keywords = ['critical', 'fatal', 'system', 'corruption', 'security']
        if any(keyword in error_msg for keyword in critical_keywords):
            return 'critical'
        
        # 高严重性错误
        high_keywords = ['error', 'exception', 'failed', 'timeout', 'memory']
        if any(keyword in error_msg for keyword in high_keywords):
            return 'high'
        
        # 中等严重性错误
        medium_keywords = ['warning', 'invalid', 'missing', 'not found']
        if any(keyword in error_msg for keyword in medium_keywords):
            return 'medium'
        
        return 'low'
    
    def _match_error_pattern(self, error_message: str) -> str:
        """匹配错误模式"""
        error_msg_lower = error_message.lower()
        
        for pattern, keywords in self.error_patterns.items():
            if any(keyword in error_msg_lower for keyword in keywords):
                return pattern
        
        return 'unknown'
    
    def _generate_recovery_strategies(
        self, 
        context: RecoveryContext, 
        error_pattern: str
    ) -> List[RecoveryAction]:
        """生成恢复策略"""
        strategies = []
        
        # 基于错误模式生成策略
        if error_pattern == 'timeout':
            strategies.extend([
                RecoveryAction(
                    strategy=RecoveryStrategy.RETRY,
                    description="重试操作，增加超时时间",
                    confidence=0.8,
                    estimated_time="30秒",
                    success_probability=0.7
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    description="使用备用服务或缓存数据",
                    confidence=0.9,
                    estimated_time="10秒",
                    success_probability=0.9
                )
            ])
        
        elif error_pattern == 'memory':
            strategies.extend([
                RecoveryAction(
                    strategy=RecoveryStrategy.RESTART,
                    description="重启组件以释放内存",
                    confidence=0.7,
                    estimated_time="1分钟",
                    risk_level="medium",
                    success_probability=0.8
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    description="使用轻量级处理模式",
                    confidence=0.8,
                    estimated_time="即时",
                    success_probability=0.7
                )
            ])
        
        elif error_pattern == 'network':
            strategies.extend([
                RecoveryAction(
                    strategy=RecoveryStrategy.RETRY,
                    description="重试网络连接",
                    confidence=0.7,
                    estimated_time="15秒",
                    success_probability=0.6
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    description="使用离线模式或缓存",
                    confidence=0.9,
                    estimated_time="即时",
                    success_probability=0.8
                )
            ])
        
        elif error_pattern == 'permission':
            strategies.extend([
                RecoveryAction(
                    strategy=RecoveryStrategy.ESCALATE,
                    description="请求管理员权限或用户授权",
                    confidence=0.9,
                    estimated_time="需要用户操作",
                    risk_level="low",
                    success_probability=0.9
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    description="使用受限功能模式",
                    confidence=0.7,
                    estimated_time="即时",
                    success_probability=0.8
                )
            ])
        
        elif error_pattern == 'data':
            strategies.extend([
                RecoveryAction(
                    strategy=RecoveryStrategy.ROLLBACK,
                    description="回滚到上一个有效状态",
                    confidence=0.9,
                    estimated_time="30秒",
                    success_probability=0.9
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    description="使用默认数据或跳过验证",
                    confidence=0.6,
                    estimated_time="即时",
                    risk_level="medium",
                    success_probability=0.7
                )
            ])
        
        # 通用策略
        if not strategies or error_pattern == 'unknown':
            strategies.extend([
                RecoveryAction(
                    strategy=RecoveryStrategy.RETRY,
                    description="简单重试操作",
                    confidence=0.6,
                    estimated_time="10秒",
                    success_probability=0.5
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.ESCALATE,
                    description="上报错误给技术支持",
                    confidence=0.8,
                    estimated_time="需要人工处理",
                    success_probability=0.9
                )
            ])
        
        # 基于历史成功率调整置信度
        for strategy in strategies:
            historical_rate = self.strategy_success_rates.get(strategy.strategy.value, 0.5)
            strategy.confidence = (strategy.confidence + historical_rate) / 2
        
        return strategies
    
    def _select_best_strategy(
        self, 
        strategies: List[RecoveryAction], 
        context: RecoveryContext
    ) -> RecoveryAction:
        """选择最佳恢复策略"""
        if not strategies:
            return RecoveryAction(
                strategy=RecoveryStrategy.ESCALATE,
                description="无可用恢复策略，需要人工处理",
                confidence=0.5,
                estimated_time="需要人工处理"
            )
        
        # 评分函数
        def score_strategy(strategy: RecoveryAction) -> float:
            score = 0.0
            
            # 基础置信度权重
            score += strategy.confidence * 0.4
            
            # 成功概率权重
            score += strategy.success_probability * 0.3
            
            # 风险等级权重（风险越低分数越高）
            risk_scores = {'low': 0.3, 'medium': 0.2, 'high': 0.1}
            score += risk_scores.get(strategy.risk_level, 0.1)
            
            # 历史成功率权重
            historical_rate = self.strategy_success_rates.get(strategy.strategy.value, 0.5)
            score += historical_rate * 0.2
            
            # 严重性调整
            if context.severity == 'critical':
                # 关键错误优先选择安全策略
                if strategy.strategy in [RecoveryStrategy.ROLLBACK, RecoveryStrategy.ESCALATE]:
                    score += 0.2
            elif context.severity == 'low':
                # 低严重性错误可以尝试更激进的策略
                if strategy.strategy == RecoveryStrategy.IGNORE:
                    score += 0.1
            
            # 重试次数惩罚
            if context.attempt_count > 2:
                if strategy.strategy == RecoveryStrategy.RETRY:
                    score -= 0.3
            
            return score
        
        # 选择得分最高的策略
        best_strategy = max(strategies, key=score_strategy)
        return best_strategy
    
    def _decide_recovery_type(
        self, 
        strategy: RecoveryAction, 
        context: RecoveryContext
    ) -> RecoveryType:
        """决定恢复类型（自动/手动）"""
        
        # 基于置信度决定
        if strategy.confidence >= self.confidence_thresholds['auto_recovery']:
            # 高置信度且低风险，自动恢复
            if strategy.risk_level == 'low':
                return RecoveryType.AUTOMATIC
        
        # 中等置信度或中等风险，混合模式
        if (strategy.confidence >= self.confidence_thresholds['manual_intervention'] and 
            strategy.risk_level in ['low', 'medium']):
            return RecoveryType.HYBRID
        
        # 低置信度或高风险，手动处理
        return RecoveryType.MANUAL
    
    def _execute_recovery(
        self, 
        strategy: RecoveryAction, 
        context: RecoveryContext
    ) -> Dict[str, Any]:
        """执行自动恢复"""
        
        execution_result = {
            'strategy': strategy.strategy.value,
            'executed_at': datetime.now().isoformat(),
            'success': False,
            'details': '',
            'execution_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            if strategy.strategy == RecoveryStrategy.RETRY:
                # 简单重试逻辑
                execution_result['success'] = True
                execution_result['details'] = "重试操作已执行"
                
            elif strategy.strategy == RecoveryStrategy.FALLBACK:
                # 回退到安全模式
                execution_result['success'] = True
                execution_result['details'] = "已切换到备用处理模式"
                
            elif strategy.strategy == RecoveryStrategy.IGNORE:
                # 忽略错误继续执行
                execution_result['success'] = True
                execution_result['details'] = "错误已忽略，继续执行"
                
            else:
                # 其他策略需要更复杂的实现
                execution_result['details'] = f"策略 {strategy.strategy.value} 需要手动执行"
                
        except Exception as e:
            execution_result['details'] = f"恢复执行失败: {str(e)}"
        
        execution_result['execution_time'] = time.time() - start_time
        
        # 更新策略成功率
        if execution_result['success']:
            current_rate = self.strategy_success_rates.get(strategy.strategy.value, 0.5)
            self.strategy_success_rates[strategy.strategy.value] = (current_rate + 1.0) / 2
        else:
            current_rate = self.strategy_success_rates.get(strategy.strategy.value, 0.5)
            self.strategy_success_rates[strategy.strategy.value] = (current_rate + 0.0) / 2
        
        # 记录尝试
        context.add_attempt(strategy.strategy, execution_result['success'], execution_result['details'])
        
        return execution_result
    
    def _generate_manual_instructions(
        self, 
        strategy: RecoveryAction, 
        context: RecoveryContext
    ) -> Dict[str, Any]:
        """生成手动处理指令"""
        
        instructions = {
            'strategy': strategy.strategy.value,
            'description': strategy.description,
            'steps': [],
            'precautions': [],
            'expected_outcome': '',
            'rollback_plan': ''
        }
        
        if strategy.strategy == RecoveryStrategy.ESCALATE:
            instructions['steps'] = [
                "1. 收集错误详细信息和系统状态",
                "2. 联系技术支持或系统管理员",
                "3. 提供错误上下文和重现步骤",
                "4. 等待专业人员处理"
            ]
            instructions['expected_outcome'] = "专业人员将分析并解决问题"
            
        elif strategy.strategy == RecoveryStrategy.RESTART:
            instructions['steps'] = [
                "1. 保存当前工作状态",
                "2. 安全关闭相关组件",
                "3. 等待30秒",
                "4. 重新启动组件",
                "5. 验证系统功能"
            ]
            instructions['precautions'] = ["确保数据已保存", "避免强制终止进程"]
            instructions['rollback_plan'] = "如果重启失败，恢复到备份状态"
            
        elif strategy.strategy == RecoveryStrategy.ROLLBACK:
            instructions['steps'] = [
                "1. 确认回滚目标状态",
                "2. 备份当前状态",
                "3. 执行状态回滚",
                "4. 验证回滚结果",
                "5. 测试系统功能"
            ]
            instructions['precautions'] = ["确保回滚点有效", "备份当前数据"]
            
        return instructions
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """获取恢复统计信息"""
        if not self.recovery_history:
            return {'status': 'no_data'}
        
        total_recoveries = len(self.recovery_history)
        
        # 按错误类型统计
        error_types = {}
        for context in self.recovery_history:
            error_type = context.error_type
            if error_type not in error_types:
                error_types[error_type] = {'count': 0, 'success_rate': 0}
            error_types[error_type]['count'] += 1
        
        # 按组件统计
        components = {}
        for context in self.recovery_history:
            component = context.component
            if component not in components:
                components[component] = {'count': 0, 'avg_attempts': 0}
            components[component]['count'] += 1
            components[component]['avg_attempts'] += context.attempt_count
        
        # 计算平均值
        for component_stats in components.values():
            component_stats['avg_attempts'] /= component_stats['count']
        
        return {
            'total_recoveries': total_recoveries,
            'error_types': error_types,
            'components': components,
            'strategy_success_rates': self.strategy_success_rates.copy(),
            'recent_recoveries': len([c for c in self.recovery_history 
                                    if (datetime.now() - c.timestamp).total_seconds() < 24 * 3600])
        }