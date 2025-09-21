#!/usr/bin/env python3
"""
Improved Single Post Crawler
More precise extraction for Tistory posts
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

class ImprovedSingleCrawler:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome driver"""
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
        """Crawl a single post with precise extraction"""
        print(f"🚀 Crawling: {post_url}")
        
        if not self.setup_driver():
            return None
        
        try:
            # Navigate to the post
            self.driver.get(post_url)
            time.sleep(5)
            
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
            
            # Wait for page to fully load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to load all content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Extract title - try multiple selectors
            title_selectors = [
                "h1", ".post-title", ".entry-title", ".title",
                ".post-header h1", ".entry-header h1",
                "article h1", "main h1"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_elem.text.strip()
                    if title_text and len(title_text) > 5 and "happy8825" not in title_text:
                        post_data['title'] = title_text
                        print(f"✓ Title: {title_text}")
                        break
                except:
                    continue
            
            # Extract date - look for Korean date format
            date_patterns = [
                r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})',  # 2024. 6. 29
                r'(\d{4})\.(\d{1,2})\.(\d{1,2})',        # 2024.6.29
                r'(\d{4})-(\d{1,2})-(\d{1,2})'           # 2024-6-29
            ]
            
            page_text = self.driver.page_source
            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    year, month, day = match.groups()
                    post_data['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    print(f"✓ Date: {post_data['date']}")
                    break
            
            # Extract category - look for specific Tistory category elements
            try:
                # Look for category links
                category_elem = self.driver.find_element(By.CSS_SELECTOR, "a[href*='/category/']")
                if category_elem:
                    post_data['category'] = category_elem.text.strip()
                    print(f"✓ Category: {post_data['category']}")
            except:
                pass
            
            # Extract tags
            try:
                tag_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[rel='tag']")
                for tag_elem in tag_elements:
                    tag_text = tag_elem.text.strip()
                    if tag_text and tag_text not in post_data['tags']:
                        post_data['tags'].append(tag_text)
                if post_data['tags']:
                    print(f"✓ Tags: {post_data['tags']}")
            except:
                pass
            
            # Extract main content - focus on article content
            content_selectors = [
                ".tt_article_useless_p_margin",  # Tistory specific
                ".entry-content",
                ".post-content",
                "article .content",
                ".post-body",
                "main article"
            ]
            
            content_html = ""
            
            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Clean up unwanted elements
                    self.driver.execute_script("""
                        var elem = arguments[0];
                        var unwanted = elem.querySelectorAll('script, style, nav, footer, .ads, .advertisement, .social-share, .sidebar, .widget, .navigation, .menu, .header, .tistorytoolbar');
                        unwanted.forEach(function(el) { el.remove(); });
                        
                        // Remove Tistory specific unwanted elements
                        var tistoryUnwanted = elem.querySelectorAll('.post-navigation, .post-meta, .post-tags, .post-category, .post-date');
                        tistoryUnwanted.forEach(function(el) { el.remove(); });
                    """, content_elem)
                    
                    temp_content = content_elem.get_attribute('innerHTML')
                    
                    # Extract images from this content
                    img_elements = content_elem.find_elements(By.TAG_NAME, 'img')
                    for img in img_elements:
                        src = img.get_attribute('src')
                        alt = img.get_attribute('alt') or ''
                        if src and not src.startswith('data:'):
                            post_data['images'].append({'src': src, 'alt': alt})
                            print(f"✓ Image: {src}")
                    
                    if temp_content and len(temp_content.strip()) > 500:
                        content_html = temp_content
                        print(f"✓ Content found with selector: {selector}")
                        break
                        
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            # If still no content, try to get the main article area
            if not content_html or len(content_html.strip()) < 500:
                try:
                    # Look for the main content area more broadly
                    article_elem = self.driver.find_element(By.CSS_SELECTOR, "article")
                    
                    # Remove unwanted elements
                    self.driver.execute_script("""
                        var elem = arguments[0];
                        var unwanted = elem.querySelectorAll('script, style, nav, footer, .ads, .sidebar, .widget, .navigation, .menu, .header, .tistorytoolbar, .post-navigation, .post-meta, .post-tags, .post-category, .post-date');
                        unwanted.forEach(function(el) { el.remove(); });
                    """, article_elem)
                    
                    content_html = article_elem.get_attribute('innerHTML')
                    
                    # Extract images
                    img_elements = article_elem.find_elements(By.TAG_NAME, 'img')
                    for img in img_elements:
                        src = img.get_attribute('src')
                        alt = img.get_attribute('alt') or ''
                        if src and not src.startswith('data:'):
                            post_data['images'].append({'src': src, 'alt': alt})
                            print(f"✓ Image in article: {src}")
                    
                    print(f"✓ Content extracted from article element")
                    
                except Exception as e:
                    print(f"Article extraction failed: {e}")
                    content_html = "Content extraction failed"
            
            post_data['content'] = content_html
            
            # Set defaults if not found
            if not post_data['date']:
                post_data['date'] = datetime.now().strftime('%Y-%m-%d')
            if not post_data['category']:
                post_data['category'] = "General"
            
            print(f"\n📊 Final Results:")
            print(f"  Title: {post_data['title']}")
            print(f"  Date: {post_data['date']}")
            print(f"  Category: {post_data['category']}")
            print(f"  Tags: {post_data['tags']}")
            print(f"  Images: {len(post_data['images'])}")
            print(f"  Content length: {len(post_data['content'])} characters")
            
            return post_data
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def save_result(self, post_data):
        """Save the result"""
        with open("improved_test_result.json", 'w', encoding='utf-8') as f:
            json.dump(post_data, f, ensure_ascii=False, indent=2)
        print("💾 Saved to improved_test_result.json")
        
        # Create HTML preview
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_data['title']} - Improved Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .meta {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .content {{ background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        img {{ max-width: 100%; height: auto; margin: 10px 0; border: 1px solid #ddd; }}
        .images {{ margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>{post_data['title']}</h1>
    <div class="meta">
        <p><strong>URL:</strong> <a href="{post_data['url']}" target="_blank">{post_data['url']}</a></p>
        <p><strong>Date:</strong> {post_data['date']}</p>
        <p><strong>Category:</strong> {post_data['category']}</p>
        <p><strong>Tags:</strong> {', '.join(post_data['tags'])}</p>
        <p><strong>Images:</strong> {len(post_data['images'])}</p>
        <p><strong>Content length:</strong> {len(post_data['content'])} characters</p>
    </div>
    <div class="content">
        <h2>Content:</h2>
        <div>{post_data['content']}</div>
    </div>
    <div class="images">
        <h2>Images ({len(post_data['images'])}):</h2>
        {''.join([f'<img src="{img["src"]}" alt="{img["alt"]}" title="{img["alt"]}">' for img in post_data['images']])}
    </div>
</body>
</html>"""
        
        with open("improved_test_result.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("📄 Created improved_test_result.html")
    
    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    print("🧪 Improved Single Post Crawler")
    
    crawler = ImprovedSingleCrawler()
    
    try:
        post_data = crawler.crawl_single_post("https://happy8825.tistory.com/2")
        
        if post_data:
            print(f"\n✅ Success!")
            crawler.save_result(post_data)
        else:
            print("❌ Failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        crawler.close()

if __name__ == "__main__":
    main()
