"""
性能监控系统
Performance Monitor

用于跟踪模块执行时间、内存使用、调用统计和生成性能报告。
"""
import time
import threading
import psutil
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    性能监控器
    - 跟踪执行时间、内存使用、调用统计
    - 支持性能报告生成
    """
    def __init__(self):
        self._stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._process = psutil.Process()
        logger.info("Performance monitor initialized")

    def start_timer(self, key: str):
        with self._lock:
            self._stats.setdefault(key, {})['start_time'] = time.time()

    def end_timer(self, key: str):
        with self._lock:
            start = self._stats.get(key, {}).get('start_time')
            if start:
                duration = time.time() - start
                self._stats[key]['duration'] = duration
                self._stats[key]['end_time'] = time.time()
                logger.debug(f"Timer for {key}: {duration:.3f}s")

    def record_call(self, key: str, success: bool = True):
        with self._lock:
            stat = self._stats.setdefault(key, {})
            stat['calls'] = stat.get('calls', 0) + 1
            stat['success'] = stat.get('success', 0) + int(success)
            stat['fail'] = stat.get('fail', 0) + int(not success)

    def record_memory(self, key: str):
        with self._lock:
            mem = self._process.memory_info().rss / 1024 / 1024
            self._stats.setdefault(key, {})['memory_mb'] = mem
            logger.debug(f"Memory for {key}: {mem:.2f}MB")

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: v.copy() for k, v in self._stats.items()}

    def generate_report(self) -> Dict[str, Any]:
        with self._lock:
            report = {
                'timestamp': time.time(),
                'summary': {},
                'details': self.get_stats()
            }
            for key, stat in self._stats.items():
                report['summary'][key] = {
                    'calls': stat.get('calls', 0),
                    'success': stat.get('success', 0),
                    'fail': stat.get('fail', 0),
                    'avg_duration': stat.get('duration', 0),
                    'memory_mb': stat.get('memory_mb', 0)
                }
            logger.info("Performance report generated")
            return report

    def monitor_execution(self, func):
        """Decorator to monitor function execution"""
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            self.start_timer(func_name)
            self.record_memory(func_name)
            
            try:
                result = func(*args, **kwargs)
                self.record_call(func_name, success=True)
                return result
            except Exception as e:
                self.record_call(func_name, success=False)
                raise
            finally:
                self.end_timer(func_name)
        
        return wrapper

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics"""
        with self._lock:
            total_calls = sum(stat.get('calls', 0) for stat in self._stats.values())
            total_success = sum(stat.get('success', 0) for stat in self._stats.values())
            
            return {
                'total_functions': len(self._stats),
                'total_calls': total_calls,
                'success_rate': (total_success / total_calls * 100) if total_calls > 0 else 0,
                'function_stats': {k: v.copy() for k, v in self._stats.items()}
            }
