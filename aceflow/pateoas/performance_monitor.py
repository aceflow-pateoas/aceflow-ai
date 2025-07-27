"""
PATEOAS性能监控系统
提供全面的性能跟踪、指标收集和警报功能
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .config import get_config
from .utils import ensure_directory


@dataclass
class PerformanceMetric:
    """性能指标数据模型"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    category: str = "general"
    unit: str = ""
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    def is_warning(self) -> bool:
        """检查是否达到警告阈值"""
        return self.threshold_warning is not None and self.value >= self.threshold_warning
    
    def is_critical(self) -> bool:
        """检查是否达到关键阈值"""
        return self.threshold_critical is not None and self.value >= self.threshold_critical


@dataclass
class ComponentPerformance:
    """组件性能数据"""
    component_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    last_call_time: Optional[datetime] = None
    
    def add_call(self, execution_time: float, success: bool = True):
        """添加调用记录"""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        
        self.total_time += execution_time
        self.average_time = self.total_time / self.total_calls
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.last_call_time = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.successful_calls / max(1, self.total_calls)
    
    @property
    def failure_rate(self) -> float:
        """失败率"""
        return self.failed_calls / max(1, self.total_calls)


class PATEOASPerformanceMonitor:
    """PATEOAS性能监控器"""
    
    def __init__(self, project_id: str = "default"):
        self.project_id = project_id
        self.config = get_config()
        
        # 性能数据存储
        self.metrics_history: List[PerformanceMetric] = []
        self.component_performance: Dict[str, ComponentPerformance] = {}
        
        # 实时指标
        self.current_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'decision_accuracy': 0.8,
            'user_satisfaction': 0.8,
            'memory_efficiency': 0.8,
            'system_health_score': 0.8
        }
        
        # 警报配置
        self.alert_thresholds = {
            'response_time_warning': 2.0,  # 秒
            'response_time_critical': 5.0,
            'success_rate_warning': 0.8,
            'success_rate_critical': 0.6,
            'memory_efficiency_warning': 0.6,
            'memory_efficiency_critical': 0.4
        }
        
        # 存储目录
        self.metrics_dir = ensure_directory(Path(self.config.state_storage_path) / "metrics")
        self.metrics_file = self.metrics_dir / f"{project_id}_performance.json"
        
        # 加载历史数据
        self._load_metrics_history()
    
    def start_operation(self, operation_name: str) -> str:
        """开始操作计时"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        self._operation_start_times = getattr(self, '_operation_start_times', {})
        self._operation_start_times[operation_id] = time.time()
        return operation_id
    
    def end_operation(self, operation_id: str, component_name: str, success: bool = True):
        """结束操作计时并记录性能"""
        start_times = getattr(self, '_operation_start_times', {})
        if operation_id not in start_times:
            return
        
        execution_time = time.time() - start_times[operation_id]
        del start_times[operation_id]
        
        # 更新组件性能
        if component_name not in self.component_performance:
            self.component_performance[component_name] = ComponentPerformance(component_name)
        
        self.component_performance[component_name].add_call(execution_time, success)
        
        # 更新全局指标
        self._update_global_metrics(execution_time, success)
        
        # 记录性能指标
        self._record_metric(
            name=f"{component_name}_execution_time",
            value=execution_time,
            category="performance",
            unit="seconds"
        )
    
    def record_decision_accuracy(self, accuracy: float):
        """记录决策准确性"""
        self.current_metrics['decision_accuracy'] = accuracy
        self._record_metric("decision_accuracy", accuracy, "quality", "ratio")
    
    def record_user_satisfaction(self, satisfaction: float):
        """记录用户满意度"""
        self.current_metrics['user_satisfaction'] = satisfaction
        self._record_metric("user_satisfaction", satisfaction, "quality", "ratio")
    
    def record_memory_efficiency(self, efficiency: float):
        """记录记忆效率"""
        self.current_metrics['memory_efficiency'] = efficiency
        self._record_metric("memory_efficiency", efficiency, "performance", "ratio")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        return {
            'current_metrics': self.current_metrics.copy(),
            'component_performance': {
                name: {
                    'success_rate': comp.success_rate,
                    'average_time': comp.average_time,
                    'total_calls': comp.total_calls,
                    'last_call': comp.last_call_time.isoformat() if comp.last_call_time else None
                }
                for name, comp in self.component_performance.items()
            },
            'system_health': self._calculate_system_health(),
            'alerts': self._check_alerts(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取指标历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            {
                'name': metric.name,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'category': metric.category,
                'unit': metric.unit
            }
            for metric in self.metrics_history
            if metric.timestamp >= cutoff_time
        ]
        
        return recent_metrics
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'project_id': self.project_id,
            'summary': self.get_performance_summary(),
            'trends': self._analyze_performance_trends(),
            'recommendations': self._generate_performance_recommendations(),
            'component_analysis': self._analyze_component_performance(),
            'alert_history': self._get_recent_alerts()
        }
        
        return report
    
    def _update_global_metrics(self, execution_time: float, success: bool):
        """更新全局指标"""
        self.current_metrics['total_requests'] += 1
        
        if success:
            self.current_metrics['successful_requests'] += 1
        else:
            self.current_metrics['failed_requests'] += 1
        
        # 更新平均响应时间
        total_requests = self.current_metrics['total_requests']
        current_avg = self.current_metrics['average_response_time']
        self.current_metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
        
        # 更新系统健康分数
        self.current_metrics['system_health_score'] = self._calculate_system_health()
    
    def _record_metric(self, name: str, value: float, category: str, unit: str):
        """记录性能指标"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            category=category,
            unit=unit,
            threshold_warning=self.alert_thresholds.get(f"{name}_warning"),
            threshold_critical=self.alert_thresholds.get(f"{name}_critical")
        )
        
        self.metrics_history.append(metric)
        
        # 保持历史记录在合理范围内
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-5000:]
        
        # 定期保存
        if len(self.metrics_history) % 100 == 0:
            self._save_metrics_history()
    
    def _calculate_system_health(self) -> float:
        """计算系统健康分数"""
        factors = {
            'success_rate': self._get_success_rate(),
            'response_time': min(1.0, 2.0 / max(0.1, self.current_metrics['average_response_time'])),
            'decision_accuracy': self.current_metrics['decision_accuracy'],
            'user_satisfaction': self.current_metrics['user_satisfaction'],
            'memory_efficiency': self.current_metrics['memory_efficiency']
        }
        
        weights = {
            'success_rate': 0.3,
            'response_time': 0.2,
            'decision_accuracy': 0.2,
            'user_satisfaction': 0.15,
            'memory_efficiency': 0.15
        }
        
        health_score = sum(factors[key] * weights[key] for key in factors)
        return min(1.0, max(0.0, health_score))
    
    def _get_success_rate(self) -> float:
        """获取成功率"""
        total = self.current_metrics['total_requests']
        if total == 0:
            return 1.0
        return self.current_metrics['successful_requests'] / total
    
    def _check_alerts(self) -> List[Dict[str, Any]]:
        """检查警报"""
        alerts = []
        
        # 检查响应时间
        avg_time = self.current_metrics['average_response_time']
        if avg_time >= self.alert_thresholds['response_time_critical']:
            alerts.append({
                'type': 'critical',
                'metric': 'response_time',
                'value': avg_time,
                'threshold': self.alert_thresholds['response_time_critical'],
                'message': f'平均响应时间过高: {avg_time:.2f}s'
            })
        elif avg_time >= self.alert_thresholds['response_time_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'response_time',
                'value': avg_time,
                'threshold': self.alert_thresholds['response_time_warning'],
                'message': f'平均响应时间较高: {avg_time:.2f}s'
            })
        
        # 检查成功率
        success_rate = self._get_success_rate()
        if success_rate <= self.alert_thresholds['success_rate_critical']:
            alerts.append({
                'type': 'critical',
                'metric': 'success_rate',
                'value': success_rate,
                'threshold': self.alert_thresholds['success_rate_critical'],
                'message': f'成功率过低: {success_rate:.2%}'
            })
        elif success_rate <= self.alert_thresholds['success_rate_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'success_rate',
                'value': success_rate,
                'threshold': self.alert_thresholds['success_rate_warning'],
                'message': f'成功率较低: {success_rate:.2%}'
            })
        
        return alerts
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趋势"""
        if len(self.metrics_history) < 10:
            return {'status': 'insufficient_data'}
        
        # 分析最近的趋势
        recent_metrics = self.metrics_history[-50:]
        
        # 按类别分组
        by_category = {}
        for metric in recent_metrics:
            if metric.category not in by_category:
                by_category[metric.category] = []
            by_category[metric.category].append(metric)
        
        trends = {}
        for category, metrics in by_category.items():
            if len(metrics) >= 5:
                values = [m.value for m in metrics]
                # 简单的趋势分析
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)
                
                if avg_second > avg_first * 1.1:
                    trend = 'improving'
                elif avg_second < avg_first * 0.9:
                    trend = 'declining'
                else:
                    trend = 'stable'
                
                trends[category] = {
                    'trend': trend,
                    'change_percentage': ((avg_second - avg_first) / avg_first) * 100,
                    'sample_size': len(metrics)
                }
        
        return trends
    
    def _generate_performance_recommendations(self) -> List[str]:
        """生成性能建议"""
        recommendations = []
        
        # 基于当前指标生成建议
        if self.current_metrics['average_response_time'] > 1.0:
            recommendations.append("考虑优化响应时间，可能需要缓存或异步处理")
        
        if self._get_success_rate() < 0.9:
            recommendations.append("成功率较低，建议检查错误处理和异常恢复机制")
        
        if self.current_metrics['memory_efficiency'] < 0.7:
            recommendations.append("记忆效率较低，建议优化记忆索引和检索算法")
        
        if self.current_metrics['decision_accuracy'] < 0.8:
            recommendations.append("决策准确性有待提升，建议增强上下文分析和推理链")
        
        # 基于组件性能生成建议
        for name, comp in self.component_performance.items():
            if comp.average_time > 0.5:
                recommendations.append(f"{name}组件响应较慢，建议进行性能优化")
            
            if comp.success_rate < 0.9:
                recommendations.append(f"{name}组件成功率较低，建议增强错误处理")
        
        return recommendations
    
    def _analyze_component_performance(self) -> Dict[str, Any]:
        """分析组件性能"""
        analysis = {}
        
        for name, comp in self.component_performance.items():
            analysis[name] = {
                'performance_score': min(1.0, comp.success_rate * (1.0 / max(0.1, comp.average_time))),
                'reliability': comp.success_rate,
                'efficiency': 1.0 / max(0.1, comp.average_time),
                'usage_frequency': comp.total_calls,
                'status': self._get_component_status(comp)
            }
        
        return analysis
    
    def _get_component_status(self, comp: ComponentPerformance) -> str:
        """获取组件状态"""
        if comp.success_rate >= 0.95 and comp.average_time <= 0.5:
            return 'excellent'
        elif comp.success_rate >= 0.9 and comp.average_time <= 1.0:
            return 'good'
        elif comp.success_rate >= 0.8 and comp.average_time <= 2.0:
            return 'fair'
        else:
            return 'poor'
    
    def _get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取最近的警报"""
        # 简化实现，返回当前警报
        return self._check_alerts()
    
    def _load_metrics_history(self):
        """加载指标历史"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 恢复指标历史
                for metric_data in data.get('metrics_history', []):
                    metric = PerformanceMetric(
                        name=metric_data['name'],
                        value=metric_data['value'],
                        timestamp=datetime.fromisoformat(metric_data['timestamp']),
                        category=metric_data.get('category', 'general'),
                        unit=metric_data.get('unit', '')
                    )
                    self.metrics_history.append(metric)
                
                # 恢复当前指标
                if 'current_metrics' in data:
                    self.current_metrics.update(data['current_metrics'])
                    
            except Exception as e:
                print(f"加载性能指标历史失败: {e}")
    
    def _save_metrics_history(self):
        """保存指标历史"""
        try:
            data = {
                'current_metrics': self.current_metrics,
                'metrics_history': [
                    {
                        'name': metric.name,
                        'value': metric.value,
                        'timestamp': metric.timestamp.isoformat(),
                        'category': metric.category,
                        'unit': metric.unit
                    }
                    for metric in self.metrics_history[-1000:]  # 只保存最近1000条
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存性能指标历史失败: {e}")