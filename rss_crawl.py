#!/usr/bin/env python3
"""
Tistory RSS Crawler
Uses RSS feed to get post information, then crawls individual posts
"""

import requests
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Selenium not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'selenium'])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TistoryRSSCrawler:
    def __init__(self):
        self.base_url = "https://happy8825.tistory.com"
        self.rss_url = f"{self.base_url}/rss"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def get_posts_from_rss(self):
        """Get post information from RSS feed"""
        print("Fetching RSS feed...")
        
        try:
            response = self.session.get(self.rss_url)
            response.raise_for_status()
            
            # Parse RSS XML
            root = ET.fromstring(response.content)
            
            posts = []
            
            # Handle different RSS formats
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//entry')
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    date_elem = item.find('pubDate') or item.find('published')
                    description_elem = item.find('description') or item.find('summary')
                    
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text.strip() if title_elem.text else ""
                        link = link_elem.text.strip() if link_elem.text else ""
                        
                        if title and link and title != "글쓰기":
                            post_info = {
                                'title': title,
                                'url': link,
                                'date': '',
                                'description': ''
                            }
                            
                            if date_elem is not None and date_elem.text:
                                post_info['date'] = self.parse_rss_date(date_elem.text.strip())
                            
                            if description_elem is not None and description_elem.text:
                                post_info['description'] = description_elem.text.strip()
                            
                            posts.append(post_info)
                            
                except Exception as e:
                    continue
            
            print(f"Found {len(posts)} posts in RSS feed")
            return posts
            
        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return []
    
    def parse_rss_date(self, date_str):
        """Parse RSS date format"""
        try:
            # Try different date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S GMT',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # Fallback: extract date from string
            date_match = re.search(r'(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})', date_str)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
        except Exception:
            pass
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            return True
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return False
    
    def crawl_post_content(self, post_url):
        """Crawl individual post content using Selenium"""
        if not self.driver:
            if not self.setup_driver():
                return None
        
        try:
            print(f"Crawling content from: {post_url}")
            self.driver.get(post_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)
            
            # Extract content
            content_selectors = [
                ".entry-content",
                ".post-content",
                ".content",
                ".tt_article_useless_p_margin",
                "article",
                ".post"
            ]
            
            content_html = ""
            images = []
            
            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Remove unwanted elements
                    self.driver.execute_script("""
                        var unwanted = arguments[0].querySelectorAll('script, style, nav, footer, .ads, .advertisement, .social-share');
                        unwanted.forEach(function(el) { el.remove(); });
                    """, content_elem)
                    
                    content_html = content_elem.get_attribute('innerHTML')
                    
                    # Extract images
                    img_elements = content_elem.find_elements(By.TAG_NAME, 'img')
                    for img in img_elements:
                        src = img.get_attribute('src')
                        alt = img.get_attribute('alt') or ''
                        if src:
                            images.append({'src': src, 'alt': alt})
                    
                    if content_html.strip():
                        break
                        
                except:
                    continue
            
            return {
                'content': content_html,
                'images': images
            }
            
        except Exception as e:
            print(f"Error crawling {post_url}: {e}")
            return None
    
    def crawl_all_posts(self, max_posts=10):
        """Crawl all posts using RSS + individual post crawling"""
        # Get posts from RSS
        posts = self.get_posts_from_rss()
        
        if not posts:
            print("No posts found in RSS feed")
            return []
        
        # Limit number of posts
        posts = posts[:max_posts]
        
        all_posts = []
        
        for i, post_info in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}] Processing: {post_info['title']}")
            
            # Crawl individual post content
            content_data = self.crawl_post_content(post_info['url'])
            
            if content_data:
                post_data = {
                    'title': post_info['title'],
                    'url': post_info['url'],
                    'date': post_info['date'],
                    'category': 'General',  # Default category
                    'tags': [],
                    'content': content_data['content'],
                    'images': content_data['images']
                }
                
                all_posts.append(post_data)
                print(f"✓ Successfully crawled: {post_data['title']}")
                if post_data['images']:
                    print(f"  Found {len(post_data['images'])} images")
            else:
                print(f"✗ Failed to crawl content for: {post_info['title']}")
            
            time.sleep(2)  # Be respectful
        
        return all_posts
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def save_to_blog_format(posts, output_file="pages/blog/posts.json"):
    """Save crawled posts to blog format"""
    blog_data = {
        "posts": [],
        "categories": {},
        "tags": {}
    }
    
    for i, post in enumerate(posts):
        post_id = f"post-{i+1}"
        
        # Create excerpt from HTML content
        content_text = re.sub(r'<[^>]+>', '', post['content'])
        excerpt = content_text[:200] + "..." if len(content_text) > 200 else content_text
        
        blog_post = {
            "id": post_id,
            "title": post['title'],
            "date": post['date'],
            "category": post['category'],
            "tags": post['tags'],
            "excerpt": excerpt,
            "content": post['content'],
            "images": post['images'],
            "original_url": post['url']
        }
        
        blog_data["posts"].append(blog_post)
        
        # Count categories
        category = post['category']
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
    
    print(f"\n✓ Saved {len(posts)} posts to {output_file}")

def main():
    print("🚀 Starting Tistory RSS Crawler...")
    
    crawler = TistoryRSSCrawler()
    
    try:
        # Crawl posts
        posts = crawler.crawl_all_posts(max_posts=10)
        
        if posts:
            print(f"\n✅ Successfully crawled {len(posts)} posts!")
            
            # Save to JSON
            save_to_blog_format(posts)
            
            print(f"\n🎉 Blog update complete!")
            print("Run 'npm run publish' to deploy to your website.")
            
        else:
            print("❌ No posts were crawled.")
            
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        
    finally:
        crawler.close()

if __name__ == "__main__":
    main()
