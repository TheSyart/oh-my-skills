"""
统一数据模型定义

提供 VideoResult，用于规范各平台解析器的统一返回结构：
- title：标题（去除话题标签）
- topic：话题标签（以空格分隔）
- videoId：视频唯一标识
- url：视频直链
- rawUrl：原始链接
- resource：视频来源平台
"""
from dataclasses import dataclass
from typing import Any

@dataclass
class VideoResult:
    title: str
    topic: str
    videoId: Any
    url: str
    rawUrl: str
    resource: str
