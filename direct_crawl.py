#!/usr/bin/env python3
"""
Direct Tistory Crawler
Uses known URL patterns to crawl posts directly
"""

import requests
import json
import os
import re
import time
from datetime import datetime

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

class DirectTistoryCrawler:
    def __init__(self):
        self.base_url = "https://happy8825.tistory.com"
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
    
    def get_post_urls_from_range(self, start_num=1, end_num=200):
        """Generate post URLs based on typical Tistory URL patterns"""
        post_urls = []
        
        # Try different URL patterns
        patterns = [
            f"{self.base_url}/{{num}}",  # https://happy8825.tistory.com/119
            f"{self.base_url}/entry/{{num}}",  # https://happy8825.tistory.com/entry/119
            f"{self.base_url}/post/{{num}}",  # https://happy8825.tistory.com/post/119
        ]
        
        for pattern in patterns:
            for num in range(start_num, end_num + 1):
                url = pattern.format(num=num)
                post_urls.append(url)
        
        return post_urls
    
    def test_post_url(self, url):
        """Test if a URL contains a valid post"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # Check if page contains post content
            title_elem = self.driver.find_element(By.TAG_NAME, 'title')
            title = title_elem.get_attribute('text') if title_elem else ""
            
            # Skip if it's an error page or admin page
            if any(keyword in title.lower() for keyword in ['404', 'error', 'not found', 'admin', 'login']):
                return None
            
            # Look for post content
            content_selectors = [
                ".entry-content", ".post-content", ".content", 
                ".tt_article_useless_p_margin", "article", ".post"
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if content_elem and content_elem.text.strip():
                        return {
                            'url': url,
                            'title': title,
                            'valid': True
                        }
                except:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def crawl_post_content(self, post_url, title):
        """Crawl individual post content"""
        print(f"Crawling: {title[:50]}...")
        
        try:
            self.driver.get(post_url)
            time.sleep(5)
            
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
                "[class*='date']", "[class*='time']"
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
                "[class*='category']", ".tag"
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
            
            # Extract main content
            content_selectors = [
                ".entry-content", ".post-content", ".content", 
                ".tt_article_useless_p_margin", "article", ".post"
            ]
            
            content_html = ""
            
            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Remove unwanted elements
                    self.driver.execute_script("""
                        var unwanted = arguments[0].querySelectorAll('script, style, nav, footer, .ads, .advertisement, .social-share, .sidebar, .widget, .navigation');
                        unwanted.forEach(function(el) { el.remove(); });
                    """, content_elem)
                    
                    content_html = content_elem.get_attribute('innerHTML')
                    
                    # Extract images
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
    
    def crawl_all_posts(self, start_num=100, end_num=200):
        """Crawl posts using direct URL testing"""
        print("Testing post URLs to find valid posts...")
        
        if not self.setup_driver():
            return []
        
        # Generate potential URLs
        post_urls = self.get_post_urls_from_range(start_num, end_num)
        
        valid_posts = []
        
        # Test each URL
        for i, url in enumerate(post_urls, 1):
            if i % 10 == 0:
                print(f"Testing URL {i}/{len(post_urls)}: {url}")
            
            post_info = self.test_post_url(url)
            if post_info:
                valid_posts.append(post_info)
                print(f"✓ Found valid post: {post_info['title'][:50]}...")
            
            time.sleep(1)  # Be respectful
        
        print(f"\nFound {len(valid_posts)} valid posts!")
        
        # Now crawl the content of valid posts
        all_posts = []
        
        for i, post_info in enumerate(valid_posts, 1):
            print(f"\n[{i}/{len(valid_posts)}] Crawling content...")
            
            post_data = self.crawl_post_content(post_info['url'], post_info['title'])
            
            if post_data and post_data['content'] and len(post_data['content'].strip()) > 100:
                all_posts.append(post_data)
                print(f"✓ Successfully crawled: {post_data['title'][:50]}...")
                if post_data['images']:
                    print(f"  Found {len(post_data['images'])} images")
            else:
                print(f"✗ Failed to crawl content: {post_info['title'][:50]}...")
            
            time.sleep(3)  # Be respectful
        
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
    print("🚀 Starting Direct Tistory Crawler...")
    print("This will test URL patterns to find valid posts...")
    
    crawler = DirectTistoryCrawler()
    
    try:
        # Start with a smaller range for testing
        posts = crawler.crawl_all_posts(start_num=100, end_num=150)
        
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
