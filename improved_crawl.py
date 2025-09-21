#!/usr/bin/env python3
"""
Improved Tistory Crawler
Gets all posts with complete content and images
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

class ImprovedTistoryCrawler:
    def __init__(self):
        self.base_url = "https://happy8825.tistory.com"
        self.rss_url = f"{self.base_url}/rss"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
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
    
    def get_all_post_urls(self):
        """Get all post URLs by crawling through all pages"""
        print("Getting all post URLs...")
        
        if not self.driver:
            if not self.setup_driver():
                return []
        
        all_posts = []
        page = 1
        max_pages = 20  # Increase to get more posts
        
        while page <= max_pages:
            print(f"Crawling page {page}...")
            
            # Navigate to page
            if page == 1:
                url = self.base_url
            else:
                url = f"{self.base_url}?page={page}"
            
            try:
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Scroll down to load all content
                for i in range(5):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                
                # Find post links
                post_links = []
                
                # Try multiple selectors for post links
                selectors = [
                    "a[href*='/entry/']",
                    "a[href*='/post/']",
                    "article a[href]",
                    ".post-title a",
                    ".entry-title a",
                    "h1 a", "h2 a", "h3 a"
                ]
                
                for selector in selectors:
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for link in links:
                            href = link.get_attribute('href')
                            title = link.text.strip()
                            
                            if href and ('/entry/' in href or '/post/' in href) and title and title != "글쓰기" and len(title) > 5:
                                post_links.append({
                                    'url': href,
                                    'title': title
                                })
                        
                        if post_links:
                            break
                    except:
                        continue
                
                if not post_links:
                    print(f"No posts found on page {page}, stopping...")
                    break
                
                # Add to all posts
                for post in post_links:
                    if post not in all_posts:  # Avoid duplicates
                        all_posts.append(post)
                
                print(f"Found {len(post_links)} posts on page {page}")
                page += 1
                time.sleep(2)
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
        
        print(f"Total unique posts found: {len(all_posts)}")
        return all_posts
    
    def crawl_post_content(self, post_url, title):
        """Crawl individual post content"""
        print(f"Crawling: {title[:50]}...")
        
        try:
            self.driver.get(post_url)
            time.sleep(5)  # Wait longer for content to load
            
            # Scroll to load all content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            post_data = {
                'title': title,
                'url': post_url,
                'date': '',
                'category': '',
                'tags': [],
                'content': '',
                'images': []
            }
            
            # Extract date
            date_selectors = [
                ".date", ".post-date", ".entry-date", "time",
                "[class*='date']", "[class*='time']",
                ".post-meta time", ".entry-meta time"
            ]
            
            for selector in date_selectors:
                try:
                    date_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_elem.text.strip()
                    if date_text and re.search(r'\d{4}.\d{1,2}.\d{1,2}', date_text):
                        post_data['date'] = self.parse_korean_date(date_text)
                        break
                except:
                    continue
            
            # Extract category
            category_selectors = [
                ".category", ".post-category", ".entry-category",
                "[class*='category']", ".tag", ".post-tag"
            ]
            
            for selector in category_selectors:
                try:
                    cat_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    category_text = cat_elem.text.strip()
                    if category_text and category_text not in ['카테고리', '분류']:
                        post_data['category'] = category_text
                        break
                except:
                    continue
            
            # Extract tags
            tag_selectors = [
                ".tag a", ".tags a", ".post-tag", "[class*='tag'] a",
                ".entry-tags a", ".post-tags a"
            ]
            
            for selector in tag_selectors:
                try:
                    tag_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for tag_elem in tag_elems:
                        tag_text = tag_elem.text.strip()
                        if tag_text and tag_text not in post_data['tags']:
                            post_data['tags'].append(tag_text)
                except:
                    continue
            
            # Extract main content - try multiple approaches
            content_html = ""
            
            # Method 1: Look for main content containers
            content_selectors = [
                ".entry-content",
                ".post-content", 
                ".content",
                ".tt_article_useless_p_margin",
                "article .content",
                ".post-body",
                ".entry-body",
                "main",
                "article"
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Remove unwanted elements
                    self.driver.execute_script("""
                        var unwanted = arguments[0].querySelectorAll('script, style, nav, footer, .ads, .advertisement, .social-share, .sidebar, .widget');
                        unwanted.forEach(function(el) { el.remove(); });
                    """, content_elem)
                    
                    content_html = content_elem.get_attribute('innerHTML')
                    
                    # Extract images from content
                    img_elements = content_elem.find_elements(By.TAG_NAME, 'img')
                    for img in img_elements:
                        src = img.get_attribute('src')
                        alt = img.get_attribute('alt') or ''
                        if src and not src.startswith('data:'):
                            post_data['images'].append({'src': src, 'alt': alt})
                    
                    if content_html and len(content_html.strip()) > 100:
                        break
                        
                except:
                    continue
            
            # Method 2: If no content found, try to get all text content
            if not content_html or len(content_html.strip()) < 100:
                try:
                    # Get the main content area
                    body = self.driver.find_element(By.TAG_NAME, 'body')
                    
                    # Remove navigation and sidebar elements
                    self.driver.execute_script("""
                        var unwanted = arguments[0].querySelectorAll('nav, header, footer, .sidebar, .navigation, .menu, .widget, .ads, script, style');
                        unwanted.forEach(function(el) { el.remove(); });
                    """, body)
                    
                    content_html = body.get_attribute('innerHTML')
                    
                except:
                    content_html = "Content not found"
            
            post_data['content'] = content_html
            
            # If no date found, use current date
            if not post_data['date']:
                post_data['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # If no category, use default
            if not post_data['category']:
                post_data['category'] = "General"
            
            return post_data
            
        except Exception as e:
            print(f"Error crawling {post_url}: {e}")
            return None
    
    def parse_korean_date(self, date_text):
        """Parse Korean date format to YYYY-MM-DD"""
        try:
            date_match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def crawl_all_posts(self, max_posts=50):
        """Crawl all posts with complete content"""
        # Get all post URLs
        post_links = self.get_all_post_urls()
        
        if not post_links:
            print("No posts found!")
            return []
        
        # Limit number of posts for initial test
        post_links = post_links[:max_posts]
        
        all_posts = []
        
        for i, post_info in enumerate(post_links, 1):
            print(f"\n[{i}/{len(post_links)}] Processing: {post_info['title'][:50]}...")
            
            post_data = self.crawl_post_content(post_info['url'], post_info['title'])
            
            if post_data and post_data['content'] and len(post_data['content'].strip()) > 50:
                all_posts.append(post_data)
                print(f"✓ Successfully crawled: {post_data['title'][:50]}...")
                if post_data['images']:
                    print(f"  Found {len(post_data['images'])} images")
            else:
                print(f"✗ Failed to crawl or empty content: {post_info['title'][:50]}...")
            
            time.sleep(3)  # Be respectful to the server
        
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
        excerpt = content_text[:300] + "..." if len(content_text) > 300 else content_text
        
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
    print("🚀 Starting Improved Tistory Crawler...")
    print("This will crawl ALL posts with complete content...")
    
    crawler = ImprovedTistoryCrawler()
    
    try:
        # Crawl posts (start with 20 for testing, then increase)
        posts = crawler.crawl_all_posts(max_posts=20)
        
        if posts:
            print(f"\n✅ Successfully crawled {len(posts)} posts with complete content!")
            
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
