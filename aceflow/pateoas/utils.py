"""
PATEOAS 工具函数
提供通用的工具函数和辅助方法
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


def generate_id(prefix: str = "", content: str = "") -> str:
    """生成唯一ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if content:
        # 基于内容生成哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{prefix}_{timestamp}_{content_hash}" if prefix else f"{timestamp}_{content_hash}"
    else:
        return f"{prefix}_{timestamp}" if prefix else timestamp


def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（改进的中文支持）"""
    if not text1 or not text2:
        return 0.0
    
    # 改进的分词：支持中文字符级别匹配
    def extract_tokens(text):
        tokens = set()
        # 英文单词
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        tokens.update(english_words)
        
        # 中文字符（单字）
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        tokens.update(chinese_chars)
        
        # 数字
        numbers = re.findall(r'\d+', text)
        tokens.update(numbers)
        
        return tokens
    
    tokens1 = extract_tokens(text1)
    tokens2 = extract_tokens(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    
    # 计算Jaccard相似度
    jaccard_similarity = intersection / union if union > 0 else 0.0
    
    # 如果有完全匹配的子串，给予额外加分
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    # 检查是否有共同的子串（长度>=2）
    substring_bonus = 0.0
    if len(text1) >= 2 and len(text2) >= 2:
        for i in range(len(text1) - 1):
            for j in range(2, min(len(text1) - i + 1, 6)):  # 最长检查5个字符
                substr = text1_lower[i:i+j]
                if substr in text2_lower:
                    substring_bonus = max(substring_bonus, len(substr) * 0.1)
    
    return min(1.0, jaccard_similarity + substring_bonus)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """提取关键词"""
    # 简单的关键词提取
    words = re.findall(r'\w+', text.lower())
    
    # 过滤常见停用词
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        '的', '了', '在', '是', '有', '和', '或', '但', '这', '那', '我', '你', '他'
    }
    
    # 统计词频
    word_freq = {}
    for word in words:
        if len(word) > 2 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 按频率排序并返回前N个
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]


def format_duration(seconds: float) -> str:
    """格式化时间间隔"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}小时"
    else:
        days = seconds / 86400
        return f"{days:.1f}天"


def is_recent(timestamp: datetime, hours: int = 24) -> bool:
    """检查时间戳是否在最近N小时内"""
    return datetime.now() - timestamp < timedelta(hours=hours)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default


def ensure_directory(path: Union[str, Path]) -> Path:
    """确保目录存在"""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def clean_text(text: str) -> str:
    """清理文本"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除特殊字符（保留中文、英文、数字和基本标点）
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]', '', text)
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """合并字典（深度合并）"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def calculate_confidence(factors: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    """计算置信度"""
    if not factors:
        return 0.0
    
    if weights is None:
        # 等权重
        weights = {key: 1.0 for key in factors.keys()}
    
    total_weight = sum(weights.get(key, 0) for key in factors.keys())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(
        factors[key] * weights.get(key, 0) 
        for key in factors.keys()
    )
    
    return min(1.0, max(0.0, weighted_sum / total_weight))


def analyze_task_complexity(task_description: str) -> Dict[str, Any]:
    """分析任务复杂度"""
    complexity_indicators = {
        'high': ['复杂', '困难', '挑战', '架构', '系统', '集成', '性能', '安全', '算法'],
        'medium': ['实现', '开发', '功能', '接口', '数据库', '测试', '优化'],
        'low': ['简单', '修复', '更新', '配置', '文档', '样式', '格式']
    }
    
    text = task_description.lower()
    scores = {}
    
    for level, keywords in complexity_indicators.items():
        score = sum(1 for keyword in keywords if keyword in text)
        scores[level] = score
    
    # 确定复杂度级别
    max_score = max(scores.values())
    if max_score == 0:
        complexity = 'medium'  # 默认中等复杂度
    else:
        complexity = max(scores.keys(), key=lambda k: scores[k])
    
    return {
        'level': complexity,
        'scores': scores,
        'confidence': min(1.0, max_score / 3.0)  # 基于匹配关键词数量
    }


def detect_project_type(project_path: str) -> Dict[str, Any]:
    """检测项目类型"""
    path = Path(project_path)
    
    # 检查文件类型
    file_types = {}
    for file_path in path.rglob('*'):
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            if suffix:
                file_types[suffix] = file_types.get(suffix, 0) + 1
    
    # 检查配置文件
    config_files = {
        'package.json': 'nodejs',
        'requirements.txt': 'python',
        'pom.xml': 'java',
        'Cargo.toml': 'rust',
        'go.mod': 'go',
        'composer.json': 'php'
    }
    
    detected_types = []
    for config_file, project_type in config_files.items():
        if (path / config_file).exists():
            detected_types.append(project_type)
    
    # 基于文件扩展名推断
    extension_mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.cpp': 'cpp',
        '.c': 'c'
    }
    
    for ext, count in file_types.items():
        if ext in extension_mapping and count > 5:  # 至少5个文件
            project_type = extension_mapping[ext]
            if project_type not in detected_types:
                detected_types.append(project_type)
    
    return {
        'types': detected_types,
        'file_types': file_types,
        'primary_type': detected_types[0] if detected_types else 'unknown'
    }