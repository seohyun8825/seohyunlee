#!/usr/bin/env python3
"""
Tistory Blog Crawler
Crawls posts from https://happy8825.tistory.com/ and converts them to blog format
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse

class TistoryCrawler:
    def __init__(self, base_url="https://happy8825.tistory.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page_posts(self, page=1):
        """Get posts from a specific page"""
        url = f"{self.base_url}"
        if page > 1:
            url += f"?page={page}"
            
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            return None
    
    def parse_post_list(self, html):
        """Parse the main page to get post links"""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        # Try different selectors for Tistory posts
        # Look for post containers first
        post_containers = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|item'))
        
        for container in post_containers:
            # Find title link within container
            title_link = container.find('a', href=True)
            if title_link:
                href = title_link.get('href', '')
                if '/entry/' in href or '/post/' in href:
                    full_url = urljoin(self.base_url, href)
                    title = title_link.get_text().strip()
                    
                    # Extract date from container
                    date_elem = container.find(['time', 'span'], class_=re.compile(r'date|time'))
                    date = ""
                    if date_elem:
                        date = self.parse_korean_date(date_elem.get_text().strip())
                    
                    # Extract category
                    category_elem = container.find(['span', 'a'], class_=re.compile(r'category|tag'))
                    category = ""
                    if category_elem:
                        category = category_elem.get_text().strip()
                    
                    if title and title != "글쓰기":  # Skip "글쓰기" link
                        posts.append({
                            'url': full_url,
                            'title': title,
                            'date': date,
                            'category': category,
                            'link_element': title_link
                        })
        
        # If no posts found with containers, try direct link search
        if not posts:
            post_links = soup.find_all('a', href=True)
            for link in post_links:
                href = link.get('href', '')
                if '/entry/' in href or '/post/' in href:
                    full_url = urljoin(self.base_url, href)
                    title = link.get_text().strip()
                    if title and title != "글쓰기" and len(title) > 5:  # Skip short titles and "글쓰기"
                        posts.append({
                            'url': full_url,
                            'title': title,
                            'date': "",
                            'category': "",
                            'link_element': link
                        })
        
        return posts
    
    def get_post_content(self, post_url):
        """Get full content of a specific post"""
        try:
            response = self.session.get(post_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching post {post_url}: {e}")
            return None
    
    def parse_post_detail(self, html, url):
        """Parse individual post content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = ""
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
        
        # Extract date
        date = ""
        date_elem = soup.find('time') or soup.find('span', class_=re.compile(r'date|time'))
        if date_elem:
            date_text = date_elem.get_text().strip()
            # Try to parse Korean date format
            date = self.parse_korean_date(date_text)
        
        # Extract category
        category = ""
        category_elem = soup.find('span', class_=re.compile(r'category|tag'))
        if category_elem:
            category = category_elem.get_text().strip()
        
        # Extract content
        content = ""
        content_elem = soup.find('div', class_=re.compile(r'content|entry|post')) or soup.find('article')
        if content_elem:
            content = content_elem.get_text().strip()
        
        # Extract tags
        tags = []
        tag_elements = soup.find_all('a', class_=re.compile(r'tag'))
        for tag_elem in tag_elements:
            tag_text = tag_elem.get_text().strip()
            if tag_text:
                tags.append(tag_text)
        
        return {
            'title': title,
            'date': date,
            'category': category,
            'content': content,
            'tags': tags,
            'url': url,
            'html': html
        }
    
    def parse_korean_date(self, date_text):
        """Parse Korean date format to YYYY-MM-DD"""
        try:
            # Remove Korean text and extract date
            date_match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        
        # Fallback to current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def crawl_all_posts(self, max_pages=5):
        """Crawl all posts from the blog"""
        all_posts = []
        
        for page in range(1, max_pages + 1):
            print(f"Crawling page {page}...")
            html = self.get_page_posts(page)
            if not html:
                break
                
            posts = self.parse_post_list(html)
            if not posts:
                print(f"No posts found on page {page}")
                break
            
            for post in posts:
                print(f"  Crawling: {post['title']}")
                post_html = self.get_post_content(post['url'])
                if post_html:
                    post_detail = self.parse_post_detail(post_html, post['url'])
                    if post_detail['title'] and post_detail['content']:
                        all_posts.append(post_detail)
                        time.sleep(1)  # Be respectful to the server
                else:
                    print(f"    Failed to get content for: {post['title']}")
            
            time.sleep(2)  # Be respectful between pages
        
        return all_posts

def save_posts_to_json(posts, output_file="pages/blog/posts.json"):
    """Save crawled posts to JSON format"""
    # Create blog data structure
    blog_data = {
        "posts": [],
        "categories": {},
        "tags": {}
    }
    
    for i, post in enumerate(posts):
        # Generate unique ID
        post_id = f"post-{i+1}"
        
        # Clean content for excerpt
        content = post['content']
        excerpt = content[:200] + "..." if len(content) > 200 else content
        
        # Determine category
        category = post['category'] or "General"
        
        blog_post = {
            "id": post_id,
            "title": post['title'],
            "date": post['date'],
            "category": category,
            "tags": post['tags'],
            "excerpt": excerpt,
            "content": content,
            "original_url": post['url']
        }
        
        blog_data["posts"].append(blog_post)
        
        # Count categories
        if category not in blog_data["categories"]:
            blog_data["categories"][category] = 0
        blog_data["categories"][category] += 1
        
        # Count tags
        for tag in post['tags']:
            if tag not in blog_data["tags"]:
                blog_data["tags"][tag] = 0
            blog_data["tags"][tag] += 1
    
    # Convert counts to arrays for frontend
    blog_data["categories"] = [
        {"name": name, "count": count, "color": "#667eea"} 
        for name, count in blog_data["categories"].items()
    ]
    blog_data["tags"] = [
        {"name": name, "count": count} 
        for name, count in blog_data["tags"].items()
    ]
    
    # Save to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(blog_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(posts)} posts to {output_file}")

def save_individual_posts(posts, output_dir="pages/blog/posts"):
    """Save individual posts as HTML files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for post in posts:
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', post['title'])
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{post['date']}-{safe_title}.html"
        
        # Create HTML content
        back_arrow = "←"
        
        category_html = f"<span> | 🏷️ {post['category']}</span>" if post['category'] else ""
        original_link_html = f"<span> | 🔗 <a href='{post['original_url']}' target='_blank'>Original Post</a></span>" if post['original_url'] else ""
        
        tags_html = ""
        if post['tags']:
            tag_spans = [f'<span style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 12px; margin-right: 0.5rem; font-size: 0.9rem;">#{tag}</span>' for tag in post['tags']]
            tags_html = f"<div class='tags'>{''.join(tag_spans)}</div>"
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} - Seohyun Lee Blog</title>
    <meta name="description" content="{post['excerpt'][:160]}">
    <link rel="stylesheet" href="../../styles.css">
    <style>
        body {{ 
            background: #0d0f17; 
            color: #fff; 
            font-family: 'Inter', sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 2rem;
            max-width: 800px;
            margin: 0 auto;
        }}
        .post-header {{
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 2rem;
            margin-bottom: 2rem;
        }}
        .post-meta {{
            color: #888;
            margin-bottom: 1rem;
        }}
        .post-title {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .post-content {{
            font-size: 1.1rem;
            line-height: 1.8;
            white-space: pre-wrap;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 2rem;
            color: #667eea;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        .back-link:hover {{
            background: rgba(102, 126, 234, 0.2);
        }}
    </style>
</head>
<body>
    <a href="../blog.html" class="back-link">{back_arrow} Back to Blog</a>
    
    <div class="post-header">
        <div class="post-meta">
            <span>📅 {post['date']}</span>
            {category_html}
            {original_link_html}
        </div>
        <h1 class="post-title">{post['title']}</h1>
        {tags_html}
    </div>
    
    <div class="post-content">
{post['content']}
    </div>
    
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
        <a href="../blog.html" class="back-link">{back_arrow} Back to Blog</a>
    </div>
</body>
</html>"""
        
        # Save file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Saved: {filename}")

def main():
    print("Starting Tistory blog crawl...")
    
    crawler = TistoryCrawler()
    
    # Crawl posts
    posts = crawler.crawl_all_posts(max_pages=3)  # Start with 3 pages
    
    if posts:
        print(f"\nCrawled {len(posts)} posts successfully!")
        
        # Save to JSON (for the blog listing)
        save_posts_to_json(posts)
        
        # Save individual HTML files
        save_individual_posts(posts)
        
        print("\nBlog update complete! Run 'npm run publish' to deploy.")
    else:
        print("No posts were crawled. Check the website structure.")

if __name__ == "__main__":
    main()
