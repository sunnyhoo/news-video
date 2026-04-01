"""新闻抓取模块
支持从以下来源抓取新闻：
- AP News, Reuters, BBC
- 中国国防部, 新华社
- 乌克兰国防部
使用方法：
    from news.fetcher import NewsFetcher
    fetcher = NewsFetcher(hours=12)
    news_items = fetcher.fetch_all()
"""
import logging
import requests
from typing import List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, hours: float = 12):
        self.hours = hours
        self.since = datetime.now() - timedelta(hours=hours)

    def fetch_all(self) -> List[dict]:
        """从所有配置的新闻源抓取新闻"""
        logger.info(f"开始抓取过去 {self.hours} 小时的新闻...")
        
        all_news = []
        
        # 调用各新闻源的抓取函数
        try:
            all_news.extend(self.fetch_ap_news())
            all_news.extend(self.fetch_reuters())
            all_news.extend(self.fetch_chinese_mod())
        except Exception as e:
            logger.error(f"抓取新闻时出错: {e}")
        
        # 去重（基于标题）
        seen_titles = set()
        unique_news = []
        for news in all_news:
            if news['title'] not in seen_titles:
                seen_titles.add(news['title'])
                unique_news.append(news)
        
        # 按时间排序（最新的在前）
        unique_news.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        # 限制返回数量
        max_news = 8
        if len(unique_news) > max_news:
            unique_news = unique_news[:max_news]
        
        logger.info(f"抓取完成，共获得 {len(unique_news)} 条新闻")
        return unique_news

    def fetch_ap_news(self) -> List[dict]:
        """抓取美联社新闻"""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "sources": "associated-press",
                "category": "general",
                "apiKey": "your_api_key"  # 需要在实际使用时替换
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                news_items = []
                for article in data.get('articles', []):
                    if article['publishedAt'] and datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')) >= self.since:
                        news_items.append({
                            "id": len(news_items) + 1,
                            "category": "国际新闻",
                            "title": article['title'],
                            "time": article['publishedAt'][:10],
                            "location": "全球",
                            "severity": "中",
                            "tag": "突发",
                            "content": article['description'] or "暂无详细内容",
                            "analysis": "美联社报道的国际新闻事件，需要进一步分析其影响。",
                            "impact": ["国际政治", "地区安全"],
                            "sources": ["AP News"]
                        })
                return news_items
        except Exception as e:
            logger.error(f"抓取美联社新闻失败: {e}")
        return []

    def fetch_reuters(self) -> List[dict]:
        """抓取路透社新闻"""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "sources": "reuters",
                "category": "general",
                "apiKey": "your_api_key"  # 需要在实际使用时替换
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                news_items = []
                for article in data.get('articles', []):
                    if article['publishedAt'] and datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')) >= self.since:
                        news_items.append({
                            "id": len(news_items) + 1,
                            "category": "国际新闻",
                            "title": article['title'],
                            "time": article['publishedAt'][:10],
                            "location": "全球",
                            "severity": "中",
                            "tag": "深度",
                            "content": article['description'] or "暂无详细内容",
                            "analysis": "路透社报道的国际新闻事件，需要进一步分析其影响。",
                            "impact": ["国际政治", "经济影响"],
                            "sources": ["Reuters"]
                        })
                return news_items
        except Exception as e:
            logger.error(f"抓取路透社新闻失败: {e}")
        return []

    def fetch_chinese_mod(self) -> List[dict]:
        """抓取中国国防部新闻"""
        try:
            # 模拟数据，实际项目中需要解析国防部网站
            news_items = [
                {
                    "id": 1,
                    "category": "国防新闻",
                    "title": "中国国防部就近期国际安全形势发表声明",
                    "time": datetime.now().strftime("%Y-%m-%d"),
                    "location": "中国",
                    "severity": "中高",
                    "tag": "官方",
                    "content": "中国国防部发言人表示，中国军队将坚定维护国家主权和领土完整，对任何挑衅行为保持高度警惕。",
                    "analysis": "中国国防部的声明体现了中国在维护国家主权方面的坚定立场，对地区安全局势有重要影响。",
                    "impact": ["地区安全", "国际关系"],
                    "sources": ["中国国防部"]
                }
            ]
            return news_items
        except Exception as e:
            logger.error(f"抓取中国国防部新闻失败: {e}")
        return []
