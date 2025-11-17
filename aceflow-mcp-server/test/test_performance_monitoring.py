"""
性能监控与懒加载集成测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from aceflow_mcp_server.performance.monitor import PerformanceMonitor
from aceflow_mcp_server.performance.lazy_loader import LazyLoader, LoadingProfile, LoadStrategy, LoadPriority

def test_monitor_basic():
    monitor = PerformanceMonitor()
    monitor.start_timer('core')
    time.sleep(0.05)
    monitor.end_timer('core')
    monitor.record_call('core', True)
    monitor.record_memory('core')
    report = monitor.generate_report()
    print("Performance report:", report)

def test_lazy_loader_basic():
    loader = LazyLoader()
    def dummy_module():
        time.sleep(0.02)
        return {'name': 'dummy'}
    profile = LoadingProfile(strategy=LoadStrategy.LAZY, priority=LoadPriority.NORMAL)
    loader.register_loader('dummy', dummy_module, profile)
    mod = loader.get_module('dummy')
    assert mod['name'] == 'dummy'
    stats = loader.get_loading_stats()['dummy']
    print("Lazy loading stats:", stats)

def run_all():
    print("--- 性能监控测试 ---")
    test_monitor_basic()
    print("--- 懒加载测试 ---")
    test_lazy_loader_basic()

if __name__ == "__main__":
    run_all()
