import requests
from bs4 import BeautifulSoup
import json

# List of AI news sources
news_sources = {
    "HackerNews": "https://news.ycombinator.com/",
    "TechCrunch": "https://techcrunch.com/",
    "ArXiv": "https://arxiv.org/",
}

# Function to collect news
def collect_news():
    news_items = []

    for source_name, url in news_sources.items():
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if source_name == 'HackerNews':
            items = soup.select('.storylink')
            for item in items[:10]:  # Get top 10 news
                title = item.text
                link = item['href']
                news_items.append({"category": "HackerNews", "title_EN": title, "summary": "N/A", "source": link})
        elif source_name == 'TechCrunch':
            items = soup.find_all('article')
            for item in items[:10]:  # Get top 10 news
                title = item.h2.text.strip()
                link = item.find('a')['href']
                summary = item.find('p').text.strip()
                news_items.append({"category": "TechCrunch", "title_EN": title, "summary": summary, "source": link})
        elif source_name == 'ArXiv':
            items = soup.find_all('div', class_='meta')
            for item in items[:10]:  # Get top 10 news
                title = item.a.text
                link = item.a['href']
                summary = item.find('p').text.strip() if item.find('p') else 'No summary available'
                news_items.append({"category": "ArXiv", "title_EN": title, "summary": summary, "source": link})

    return news_items

# Save news items to a JSON file
if __name__ == '__main__':
    news = collect_news()
    with open('ai_news.json', 'w') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)