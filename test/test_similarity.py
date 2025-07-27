#!/usr/bin/env python3
"""
测试相似度计算
"""

import sys
import os
import re

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

from aceflow.pateoas.utils import calculate_similarity

def debug_similarity(text1, text2):
    """调试相似度计算"""
    print(f"文本1: '{text1}'")
    print(f"文本2: '{text2}'")
    
    # 分词测试
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    print(f"分词1: {words1}")
    print(f"分词2: {words2}")
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    print(f"交集: {intersection}")
    print(f"并集: {union}")
    
    similarity = calculate_similarity(text1, text2)
    print(f"相似度: {similarity}")
    print("-" * 50)

# 测试用例
test_cases = [
    ("登录", "用户需要登录功能"),
    ("JWT", "选择JWT认证方案"),
    ("login", "user needs login function"),
    ("用户", "用户需要登录功能"),
    ("认证", "选择JWT认证方案")
]

for text1, text2 in test_cases:
    debug_similarity(text1, text2)