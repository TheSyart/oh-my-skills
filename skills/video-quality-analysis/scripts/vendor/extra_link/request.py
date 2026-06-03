"""
网络请求封装模块

目的：
- 统一封装同步与异步的 HTTP 请求逻辑
- 提供跳转解析、页面文本获取、JSON 获取等通用方法
- 降低各平台解析器对具体请求库的耦合，便于后期拓展
"""
import asyncio
import json
from typing import Optional, Dict, Any

import requests
import aiohttp

# 同步：获取最终跳转后的 URL
def resolve_url(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> str:
    resp = requests.get(url, headers=headers or {}, allow_redirects=True, timeout=timeout)
    return resp.url

# 同步：获取页面文本
def get_text(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> str:
    resp = requests.get(url, headers=headers or {}, timeout=timeout)
    resp.raise_for_status()
    return resp.text

# 同步：获取 JSON
def get_json(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: int = 20) -> Dict[str, Any]:
    resp = requests.get(url, headers=headers or {}, params=params or {}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

# 异步：获取 JSON
async def aget_json(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, cookies=None, timeout: int = 20) -> Dict[str, Any]:
    timeout_cfg = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(cookies=cookies, timeout=timeout_cfg) as session:
        async with session.get(url, headers=headers or {}, params=params or {}) as response:
            response.raise_for_status()
            return await response.json()
