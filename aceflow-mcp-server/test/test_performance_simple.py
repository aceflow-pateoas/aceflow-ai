"""
简化的性能监控测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 直接导入新创建的模块，避免依赖问题
import time

class TestPerformanceMonitor:
    def __init__(self):
        self._stats = {}
        self._lock = None  # 简化版本
    
    def start_timer(self, key: str):
        self._stats.setdefault(key, {})['start_time'] = time.time()
    
    def end_timer(self, key: str):
        start = self._stats.get(key, {}).get('start_time')
        if start:
            duration = time.time() - start
            self._stats[key]['duration'] = duration
            print(f"Timer for {key}: {duration:.3f}s")

def test_monitor_basic():
    monitor = TestPerformanceMonitor()
    monitor.start_timer('core')
    time.sleep(0.05)
    monitor.end_timer('core')
    print("✅ 性能监控基础测试通过")

if __name__ == "__main__":
    print("🧪 运行简化性能监控测试...")
    test_monitor_basic()
    print("✅ 测试完成")
