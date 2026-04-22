import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

class AINewsCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.news_list = []
        
    def collect_from_hackernews(self):
        """从HackerNews收集AI相关新闻"""
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=10)
            story_ids = response.json()[:30]
            
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_data = requests.get(story_url, timeout=10).json()
                
                if story_data.get('type') == 'story':
                    title = story_data.get('title', '')
                    if any(keyword in title.lower() for keyword in ['ai', 'machine learning', 'deep learning', 'llm', 'neural']):
                        self.news_list.append({
                            'category': 'Tech News',
                            'title': title,
                            'summary': f"Score: {story_data.get('score', 0)}",
                            'source': 'HackerNews',
                            'url': story_data.get('url', '')
                        })
        except Exception as e:
            print(f"Error collecting from HackerNews: {e}")
    
    def collect_from_arxiv(self):
        """从arXiv收集AI论文"""
        try:
            url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
            response = requests.get(url, timeout=10)
            
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.content)
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                
                if title_elem is not None:
                    self.news_list.append({
                        'category': 'Academic',
                        'title': title_elem.text,
                        'summary': summary_elem.text[:200] if summary_elem is not None else '',
                        'source': 'arXiv',
                        'url': id_elem.text if id_elem is not None else ''
                    })
        except Exception as e:
            print(f"Error collecting from arXiv: {e}")
    
    def collect_from_techcrunch(self):
        """从TechCrunch收集AI新闻"""
        try:
            url = "https://techcrunch.com/tag/artificial-intelligence/feed/"
            response = requests.get(url, timeout=10)
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            for item in root.findall('.//item')[:10]:
                title_elem = item.find('title')
                desc_elem = item.find('description')
                link_elem = item.find('link')
                
                if title_elem is not None:
                    self.news_list.append({
                        'category': 'Industry News',
                        'title': title_elem.text,
                        'summary': BeautifulSoup(desc_elem.text if desc_elem is not None else '', 'html.parser').get_text()[:200],
                        'source': 'TechCrunch',
                        'url': link_elem.text if link_elem is not None else ''
                    })
        except Exception as e:
            print(f"Error collecting from TechCrunch: {e}")
    
    def collect_from_github_trending(self):
        """从GitHub Trending收集AI项目"""
        try:
            url = "https://github.com/trending?spoken_language_code=&since=daily&d=1"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for repo in soup.find_all('article', class_='Box-row')[:10]:
                repo_link = repo.find('h2', class_='h3')
                desc = repo.find('p', class_='col-9')
                
                if repo_link:
                    self.news_list.append({
                        'category': 'GitHub Trending',
                        'title': repo_link.get_text(strip=True),
                        'summary': desc.get_text(strip=True)[:200] if desc else '',
                        'source': 'GitHub',
                        'url': 'https://github.com' + repo_link.find('a')['href']
                    })
        except Exception as e:
            print(f"Error collecting from GitHub: {e}")
    
    def generate_markdown(self):
        """生成Markdown文件"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"news/ai-news-{today}.md"
        
        # 创建news目录
        os.makedirs('news', exist_ok=True)
        
        # 按分类组织新闻
        categorized = {}
        for news in self.news_list:
            category = news['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(news)
        
        # 生成Markdown内容
        content = f"# AI News - {today}\n\n"
        content += f"**Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC+8\n\n"
        content += f"**Total News**: {len(self.news_list)} items\n\n"
        content += "---\n\n"
        
        for category, news_items in categorized.items():
            content += f"## {category}\n\n"
            for idx, news in enumerate(news_items, 1):
                content += f"### {idx}. {news['title']}\n"
                content += f"**Source**: [{news['source']}]({news['url']})\n\n"
                content += f"**Summary**: {news['summary']}\n\n"
            content += "---\n\n"
        
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ News saved to {filename}")
        return filename
    
    def run(self):
        """运行完整的新闻收集流程"""
        print("🤖 Starting AI News Collection...")
        print("📡 Collecting from multiple sources...")
        
        self.collect_from_hackernews()
        print("✓ HackerNews collected")
        
        self.collect_from_arxiv()
        print("✓ arXiv collected")
        
        self.collect_from_techcrunch()
        print("✓ TechCrunch collected")
        
        self.collect_from_github_trending()
        print("✓ GitHub Trending collected")
        
        print(f"\n📊 Total news collected: {len(self.news_list)}")
        
        self.generate_markdown()
        print("✅ News collection completed!")

if __name__ == "__main__":
    collector = AINewsCollector()
    collector.run()
