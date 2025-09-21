#!/usr/bin/env python3
"""
Single Post Test Crawler
Tests crawling one specific post with complete content and images
"""

import requests
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

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

class SinglePostCrawler:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome driver with visible browser for debugging"""
        chrome_options = Options()
        # Remove headless mode to see what's happening
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            return True
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return False
    
    def crawl_single_post(self, post_url):
        """Crawl a single post with complete content and images"""
        print(f"🚀 Crawling single post: {post_url}")
        
        if not self.setup_driver():
            return None
        
        try:
            # Navigate to the post
            print("📖 Loading post page...")
            self.driver.get(post_url)
            time.sleep(5)  # Wait for page to load
            
            # Get page title
            title = self.driver.title
            print(f"📄 Page title: {title}")
            
            # Scroll to load all content
            print("📜 Scrolling to load all content...")
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            post_data = {
                'title': '',
                'url': post_url,
                'date': '',
                'category': '',
                'tags': [],
                'content': '',
                'images': [],
                'raw_html': ''
            }
            
            # Extract title from page content
            title_selectors = [
                "h1", ".post-title", ".entry-title", "title",
                "[class*='title']", ".post-header h1"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_elem.text.strip()
                    if title_text and len(title_text) > 5 and title_text != "happy8825":
                        post_data['title'] = title_text
                        print(f"✓ Found title: {title_text}")
                        break
                except:
                    continue
            
            if not post_data['title']:
                post_data['title'] = title
            
            # Extract date
            print("📅 Extracting date...")
            date_selectors = [
                ".date", ".post-date", ".entry-date", "time",
                "[class*='date']", "[class*='time']",
                ".post-meta time", ".entry-meta time"
            ]
            
            for selector in date_selectors:
                try:
                    date_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for date_elem in date_elems:
                        date_text = date_elem.text.strip()
                        if date_text and re.search(r'\d{4}.\d{1,2}.\d{1,2}', date_text):
                            post_data['date'] = self.parse_korean_date(date_text)
                            print(f"✓ Found date: {post_data['date']}")
                            break
                    if post_data['date']:
                        break
                except:
                    continue
            
            # Extract category
            print("🏷️ Extracting category...")
            category_selectors = [
                ".category", ".post-category", ".entry-category",
                "[class*='category']", ".tag", ".post-tag"
            ]
            
            for selector in category_selectors:
                try:
                    cat_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for cat_elem in cat_elems:
                        category_text = cat_elem.text.strip()
                        if category_text and category_text not in ['카테고리', '분류', 'NLP']:
                            post_data['category'] = category_text
                            print(f"✓ Found category: {category_text}")
                            break
                    if post_data['category']:
                        break
                except:
                    continue
            
            # Extract tags
            print("🔖 Extracting tags...")
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
                            print(f"✓ Found tag: {tag_text}")
                except:
                    continue
            
            # Extract main content - try multiple approaches
            print("📝 Extracting main content...")
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
                    content_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for content_elem in content_elems:
                        # Remove unwanted elements
                        self.driver.execute_script("""
                            var unwanted = arguments[0].querySelectorAll('script, style, nav, footer, .ads, .advertisement, .social-share, .sidebar, .widget, .navigation, .menu, .header');
                            unwanted.forEach(function(el) { el.remove(); });
                        """, content_elem)
                        
                        temp_content = content_elem.get_attribute('innerHTML')
                        
                        # Extract images from this content element
                        img_elements = content_elem.find_elements(By.TAG_NAME, 'img')
                        for img in img_elements:
                            src = img.get_attribute('src')
                            alt = img.get_attribute('alt') or ''
                            if src and not src.startswith('data:'):
                                post_data['images'].append({'src': src, 'alt': alt})
                                print(f"✓ Found image: {src}")
                        
                        if temp_content and len(temp_content.strip()) > 200:
                            content_html = temp_content
                            print(f"✓ Found content with selector: {selector}")
                            break
                    
                    if content_html:
                        break
                        
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            # Method 2: If no content found, try to get body content
            if not content_html or len(content_html.strip()) < 200:
                print("🔍 Trying alternative content extraction...")
                try:
                    # Get the main content area
                    body = self.driver.find_element(By.TAG_NAME, 'body')
                    
                    # Remove navigation and sidebar elements
                    self.driver.execute_script("""
                        var unwanted = arguments[0].querySelectorAll('nav, header, footer, .sidebar, .navigation, .menu, .widget, .ads, script, style, .tistorytoolbar');
                        unwanted.forEach(function(el) { el.remove(); });
                    """, body)
                    
                    content_html = body.get_attribute('innerHTML')
                    
                    # Extract all images from body
                    img_elements = body.find_elements(By.TAG_NAME, 'img')
                    for img in img_elements:
                        src = img.get_attribute('src')
                        alt = img.get_attribute('alt') or ''
                        if src and not src.startswith('data:'):
                            post_data['images'].append({'src': src, 'alt': alt})
                            print(f"✓ Found image in body: {src}")
                    
                    print(f"✓ Extracted content from body")
                    
                except Exception as e:
                    print(f"Error extracting from body: {e}")
                    content_html = "Content extraction failed"
            
            post_data['content'] = content_html
            
            # Save raw HTML for debugging
            post_data['raw_html'] = self.driver.page_source
            
            # If no date found, use current date
            if not post_data['date']:
                post_data['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # If no category, use default
            if not post_data['category']:
                post_data['category'] = "General"
            
            print(f"\n📊 Extraction Summary:")
            print(f"  Title: {post_data['title'][:50]}...")
            print(f"  Date: {post_data['date']}")
            print(f"  Category: {post_data['category']}")
            print(f"  Tags: {post_data['tags']}")
            print(f"  Images found: {len(post_data['images'])}")
            print(f"  Content length: {len(post_data['content'])} characters")
            
            return post_data
            
        except Exception as e:
            print(f"❌ Error crawling {post_url}: {e}")
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
    
    def save_test_result(self, post_data, output_file="test_post_result.json"):
        """Save the test result to a JSON file"""
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else "."
        os.makedirs(dir_path, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved test result to {output_file}")
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def main():
    print("🧪 Single Post Test Crawler")
    print("Testing crawling of one specific post...")
    
    # Test with the specific post URL
    test_url = "https://happy8825.tistory.com/2"
    
    crawler = SinglePostCrawler()
    
    try:
        # Crawl the single post
        post_data = crawler.crawl_single_post(test_url)
        
        if post_data:
            print(f"\n✅ Successfully crawled post!")
            
            # Save test result
            crawler.save_test_result(post_data)
            
            # Create a simple HTML file to view the result
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_data['title']} - Test Result</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            line-height: 1.6;
        }}
        .meta {{ 
            background: #f5f5f5; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px;
        }}
        .content {{ 
            background: white; 
            padding: 20px; 
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .images {{ 
            margin-top: 20px; 
            padding: 15px; 
            background: #f9f9f9; 
            border-radius: 5px;
        }}
        img {{ 
            max-width: 100%; 
            height: auto; 
            margin: 10px 0;
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <h1>{post_data['title']}</h1>
    
    <div class="meta">
        <p><strong>URL:</strong> <a href="{post_data['url']}" target="_blank">{post_data['url']}</a></p>
        <p><strong>Date:</strong> {post_data['date']}</p>
        <p><strong>Category:</strong> {post_data['category']}</p>
        <p><strong>Tags:</strong> {', '.join(post_data['tags'])}</p>
        <p><strong>Images found:</strong> {len(post_data['images'])}</p>
        <p><strong>Content length:</strong> {len(post_data['content'])} characters</p>
    </div>
    
    <div class="content">
        <h2>Extracted Content:</h2>
        <div>{post_data['content']}</div>
    </div>
    
    <div class="images">
        <h2>Images Found ({len(post_data['images'])}):</h2>
        {''.join([f'<img src="{img["src"]}" alt="{img["alt"]}" title="{img["alt"]}">' for img in post_data['images']])}
    </div>
</body>
</html>"""
            
            with open("test_post_result.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 Created test_post_result.html to view the result")
            print(f"🌐 Open test_post_result.html in your browser to see the extracted content")
            
        else:
            print("❌ Failed to crawl the post.")
            
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        
    finally:
        crawler.close()

if __name__ == "__main__":
    main()
