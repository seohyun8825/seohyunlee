#!/usr/bin/env python3
"""
Final Tistory Crawler
Crawls ALL posts with complete content, images, and proper formatting
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

class FinalTistoryCrawler:
    def __init__(self):
        self.base_url = "https://happy8825.tistory.com"
        self.driver = None
        self.all_posts = []
    
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless for faster processing
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
    
    def get_all_post_urls(self, max_posts=100):
        """Get all post URLs by testing URL patterns"""
        print("🔍 Finding all post URLs...")
        
        if not self.setup_driver():
            return []
        
        found_posts = []
        tested_urls = set()
        
        # Test different URL patterns and ranges
        patterns = [
            f"{self.base_url}/{{num}}",
            f"{self.base_url}/entry/{{num}}",
        ]
        
        # Test a wide range of numbers
        for start_num in range(1, 500, 10):  # Test in batches - even wider range for 150 posts
            for pattern in patterns:
                for num in range(start_num, start_num + 10):
                    url = pattern.format(num=num)
                    
                    if url in tested_urls:
                        continue
                    tested_urls.add(url)
                    
                    try:
                        self.driver.get(url)
                        time.sleep(0.5)  # Much shorter wait for faster processing
                        
                        # Quick check if it's a valid post
                        title_elem = self.driver.find_element(By.TAG_NAME, 'title')
                        title = title_elem.get_attribute('text') if title_elem else ""
                        
                        # Skip error pages
                        if any(keyword in title.lower() for keyword in ['404', 'error', 'not found', 'admin', 'login']):
                            continue
                        
                        # Look for content
                        try:
                            content_elem = self.driver.find_element(By.CSS_SELECTOR, ".tt_article_useless_p_margin, .entry-content, article")
                            if content_elem and content_elem.text.strip():
                                found_posts.append({
                                    'url': url,
                                    'title': title,
                                    'valid': True
                                })
                                print(f"✓ Found: {title[:50]}... ({url})")
                                
                                if len(found_posts) >= max_posts:
                                    print(f"Reached limit of {max_posts} posts")
                                    return found_posts
                        except:
                            continue
                            
                    except Exception as e:
                        continue
        
        print(f"Found {len(found_posts)} valid posts")
        return found_posts
    
    def crawl_post_content(self, post_info):
        """Crawl individual post content with improved extraction"""
        url = post_info['url']
        title = post_info['title']
        
        print(f"📖 Crawling: {title[:50]}...")
        
        try:
            self.driver.get(url)
            time.sleep(1)  # Reduced wait time
            
            # Wait for content to load with shorter timeout
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("⚠️  Timeout waiting for content, proceeding anyway...")
            
            # Quick scroll and minimal wait
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Reduced wait time
            
            post_data = {
                'title': title,
                'url': url,
                'date': '',
                'category': '',
                'tags': [],
                'content': '',
                'images': []
            }
            
            # Extract date
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
                    break
            
            # Extract category
            try:
                category_elem = self.driver.find_element(By.CSS_SELECTOR, "a[href*='/category/']")
                if category_elem:
                    post_data['category'] = category_elem.text.strip()
            except:
                pass
            
            # Extract tags
            try:
                tag_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[rel='tag']")
                for tag_elem in tag_elements:
                    tag_text = tag_elem.text.strip()
                    if tag_text and tag_text not in post_data['tags']:
                        post_data['tags'].append(tag_text)
            except:
                pass
            
            # Extract main content - use the improved method
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
                    
                    if temp_content and len(temp_content.strip()) > 500:
                        content_html = temp_content
                        break
                        
                except Exception as e:
                    continue
            
            # If still no content, try article element
            if not content_html or len(content_html.strip()) < 500:
                try:
                    article_elem = self.driver.find_element(By.CSS_SELECTOR, "article")
                    
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
                    
                except Exception as e:
                    content_html = "Content extraction failed"
            
            post_data['content'] = content_html
            
            # Set defaults
            if not post_data['date']:
                post_data['date'] = datetime.now().strftime('%Y-%m-%d')
            if not post_data['category']:
                post_data['category'] = "General"
            
            print(f"✓ Success: {len(content_html)} chars, {len(post_data['images'])} images")
            return post_data
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def crawl_all_posts(self, max_posts=50):
        """Crawl all posts with complete content"""
        print(f"🚀 Starting final crawler for up to {max_posts} posts...")
        
        # Get all post URLs
        post_links = self.get_all_post_urls(max_posts)
        
        if not post_links:
            print("❌ No posts found!")
            return []
        
        print(f"📝 Found {len(post_links)} posts, starting content extraction...")
        
        all_posts = []
        
        for i, post_info in enumerate(post_links, 1):
            print(f"\n[{i}/{len(post_links)}] Processing...")
            
            post_data = self.crawl_post_content(post_info)
            
            if post_data and post_data['content'] and len(post_data['content'].strip()) > 100:
                all_posts.append(post_data)
                print(f"✅ Added: {post_data['title'][:50]}...")
            else:
                print(f"❌ Skipped: {post_info['title'][:50]}... (no content)")
            
            time.sleep(2)  # Be respectful to the server
        
        print(f"\n🎉 Successfully crawled {len(all_posts)} posts with complete content!")
        return all_posts
    
    def save_to_blog_format(self, posts, output_file="pages/blog/posts.json"):
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
            
            # Create safe filename
            safe_title = re.sub(r'[^\w\s-]', '', post['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            post_url = f"./posts/{post['date']}-{safe_title}.html"
            
            blog_post = {
                "id": post_id,
                "title": post['title'],
                "date": post['date'],
                "category": post['category'],
                "tags": post['tags'],
                "excerpt": excerpt,
                "content": post['content'],
                "images": post['images'],
                "original_url": post['url'],
                "url": post_url
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
        
        print(f"💾 Saved {len(posts)} posts to {output_file}")
    
    def create_individual_html_posts(self, posts, output_dir="pages/blog/posts"):
        """Create individual HTML files for each post"""
        print("📄 Creating individual HTML files...")
        os.makedirs(output_dir, exist_ok=True)
        
        for i, post in enumerate(posts, 1):
            # Create safe filename
            safe_title = re.sub(r'[^\w\s-]', '', post['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{post['date']}-{safe_title}.html"
            
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
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[{i}/{len(posts)}] Created: {filename}")
        
        print(f"✅ Created {len(posts)} individual HTML files!")
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def main():
    print("🚀 Final Tistory Crawler - Complete Blog Migration")
    print("This will crawl ALL posts with complete content and images...")
    
    crawler = FinalTistoryCrawler()
    
    try:
        # Crawl posts (increased to find more posts)
        posts = crawler.crawl_all_posts(max_posts=150)
        
        if posts:
            print(f"\n✅ Successfully crawled {len(posts)} posts with complete content!")
            
            # Save to JSON
            crawler.save_to_blog_format(posts)
            
            # Create individual HTML files
            crawler.create_individual_html_posts(posts)
            
            print(f"\n🎉 Blog migration complete!")
            print("Run 'npm run publish' to deploy to your website.")
            
        else:
            print("❌ No posts were crawled.")
            
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        
    finally:
        crawler.close()

if __name__ == "__main__":
    main()
