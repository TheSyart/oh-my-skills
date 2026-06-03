"""
B 站视频解析器

功能：
- 解析 BV 号（支持 b23 短链跳转）
- 获取视频详情（title、desc、cid）
- 通过原生 API 获取直链（durl），失败时使用备用 API
- 切换常用 CDN 域名以提升可用性
- 输出统一数据模型（title、topic、videoId、url）
"""
import random
import argparse
import re
from urllib.parse import urlparse, urlunparse
import asyncio
from typing import Optional
import aiohttp
import json
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import VideoResult
import request as req

async def get_bilibili_cookies(SESSDATA=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://www.bilibili.com', headers=headers) as response:
                response.raise_for_status()
                cookies = response.cookies
                if SESSDATA is not None:
                    cookies['SESSDATA'] = SESSDATA
                return cookies
        except aiohttp.ClientError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")

async def MyRequest(APIurl, params, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'application/json',
    }
    try:
        return await req.aget_json(APIurl, headers=headers, params=params, cookies=cookies)
    except Exception as err:
        print(f"HTTP error occurred: {err}")
        return None

def getSessionData():
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            return data.get('SESSDATA')
    except:
        return None

async def getCid(BV, cookies):
    APIurl = 'https://api.bilibili.com/x/player/pagelist'
    params = {
        'bvid': BV,
    }
    return await MyRequest(APIurl, params, cookies)

def CalOR(a, b):  # OR运算 二进制属性位
    return a | b

async def getVideoInfo(BV, CID, cookies):
    APIurl = 'https://api.bilibili.com/x/player/playurl'
    params = {
        'bvid': BV,
        'cid': CID,
        'qn': 120,
        'otype': 'json',
        'platform': 'html5',
        'high_quality': 1,
        'fnval': CalOR(1, 128),
        'fourk': 1
    }
    return await MyRequest(APIurl, params, cookies)

async def BiliAnalysis(BV, p=1):
    cookies = await get_bilibili_cookies(getSessionData())
    CID = await getCid(BV, cookies)
    p -= 1
    if p < 0 or p >= len(CID['data']):
        p = 0
    VideoInfo = await getVideoInfo(BV, CID['data'][p]['cid'], cookies)
    Video = {
        'BV': BV,
        'page': p + 1,
        'url': VideoInfo['data']['durl'][0]['url'],
    }
    return Video

def ChangeBiliCDN(url):
    BiliCDN = [
        "upos-sz-mirrorcos.bilivideo.com",
        "upos-sz-mirrorali.bilivideo.com",
        "upos-sz-mirror08c.bilivideo.com",
    ]
    parsed_url = urlparse(url)
    new_netloc = random.choice(BiliCDN)
    new_url = urlunparse(parsed_url._replace(netloc=new_netloc))
    return new_url

async def getVideoDetails(BV, cookies):
    APIurl = 'https://api.bilibili.com/x/web-interface/view'
    params = {'bvid': BV}
    return await MyRequest(APIurl, params, cookies)

async def extract_bv_from_url(url: str, cookies) -> str:
    m = re.search(r'BV[0-9A-Za-z]+', url)
    if m:
        return m.group(0)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url, headers=headers, allow_redirects=True) as resp:
            real = str(resp.url)
            m2 = re.search(r'BV[0-9A-Za-z]+', real)
            if m2:
                return m2.group(0)
    raise ValueError('无法从链接提取BV号')

async def extract(url: Optional[str] = None, bv: Optional[str] = None, p: int = 1) -> VideoResult:
    """
    统一提取入口：
    - 支持传入 url 或 bv
    - 返回标准化 VideoResult
    """
    cookies = await get_bilibili_cookies(getSessionData())
    if not bv:
        if not url:
            raise ValueError("必须提供 url 或 bv")
        bv = await extract_bv_from_url(url, cookies)
    details = await getVideoDetails(bv, cookies)
    if not details or details.get('code') != 0 or 'data' not in details:
        raise ValueError("获取视频详情失败")
    info = details['data']
    title = info.get('title', '')
    topic = info.get('desc', '')
    vid = await BiliAnalysis(bv, p=p)
    video_url = ChangeBiliCDN(vid['url']) if vid and vid.get('url') else ''
    return VideoResult(
        title=title,
        topic=topic,
        videoId=bv,
        url=video_url,
        rawUrl=url or bv, # url 可能是 None 如果只传了 bv
        resource="bilibili"
    )
async def main():
    parser = argparse.ArgumentParser(description='Bilibili video link extractor')
    parser.add_argument('--url', help='Bilibili video URL or short link')
    parser.add_argument('--bv', help='Bilibili BV id')
    parser.add_argument('--p', type=int, default=1, help='Page index (default 1)')
    args = parser.parse_args()

    cookies = await get_bilibili_cookies(getSessionData())
    if args.bv:
        bv = args.bv
    elif args.url:
        bv = await extract_bv_from_url(args.url, cookies)
    else:
        raise SystemExit('必须提供 --url 或 --bv')

    details = await getVideoDetails(bv, cookies)
    if not details or details.get('code') != 0 or 'data' not in details:
        raise SystemExit(json.dumps({'status': 'error', 'error': '获取视频详情失败'}, ensure_ascii=False))
    info = details['data']
    title = info.get('title', '')
    topic = info.get('desc', '')

    vid = await BiliAnalysis(bv, p=args.p)
    video_url = ChangeBiliCDN(vid['url']) if vid and vid.get('url') else ''
    result = VideoResult(title=title, topic=topic, videoId=bv, url=video_url)
    print(json.dumps({'title': result.title, 'topic': result.topic, 'videoId': result.videoId, 'url': result.url}, ensure_ascii=False))

if __name__ == '__main__':
    asyncio.run(main())
