#!/usr/bin/env python3
"""
Advanced Tistory Crawler using Selenium
Crawls complete posts with images and formatting
"""

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

class AdvancedTistoryCrawler:
    def __init__(self):
        self.base_url = "https://happy8825.tistory.com"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            print("Please install Chrome and chromedriver, or use: pip install webdriver-manager")
            raise
    
    def wait_for_page_load(self, timeout=10):
        """Wait for page to load completely"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional wait for dynamic content
        except TimeoutException:
            print("Page load timeout")
    
    def get_post_links(self):
        """Get all post links from the main page"""
        print("Loading main page...")
        self.driver.get(self.base_url)
        self.wait_for_page_load()
        
        # Scroll down to load more posts
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        post_links = []
        
        # Try multiple selectors to find post links
        selectors = [
            "a[href*='/entry/']",
            "a[href*='/post/']", 
            ".post-title a",
            ".entry-title a",
            ".post a",
            "article a",
            "h1 a",
            "h2 a",
            "h3 a"
        ]
        
        for selector in selectors:
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for link in links:
                    href = link.get_attribute('href')
                    title = link.text.strip()
                    
                    if href and '/entry/' in href and title and title != "글쓰기" and len(title) > 5:
                        post_links.append({
                            'url': href,
                            'title': title
                        })
                        
                if post_links:
                    print(f"Found {len(post_links)} posts using selector: {selector}")
                    break
                    
            except Exception as e:
                continue
        
        # Remove duplicates
        unique_posts = []
        seen_urls = set()
        for post in post_links:
            if post['url'] not in seen_urls:
                unique_posts.append(post)
                seen_urls.add(post['url'])
        
        print(f"Total unique posts found: {len(unique_posts)}")
        return unique_posts
    
    def crawl_post(self, post_url, title):
        """Crawl a single post with full content"""
        print(f"Crawling: {title}")
        
        try:
            self.driver.get(post_url)
            self.wait_for_page_load()
            
            # Extract post data
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
                ".date",
                ".post-date", 
                ".entry-date",
                "time",
                "[class*='date']",
                "[class*='time']"
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
                ".category",
                ".post-category",
                ".entry-category", 
                "[class*='category']",
                ".tag"
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
                ".tag a",
                ".tags a",
                ".post-tag",
                "[class*='tag'] a"
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
            
            # Extract content with HTML formatting
            content_selectors = [
                ".entry-content",
                ".post-content",
                ".content", 
                ".tt_article_useless_p_margin",
                "article",
                ".post"
            ]
            
            content_html = ""
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
                            post_data['images'].append({
                                'src': src,
                                'alt': alt
                            })
                    
                    if content_html.strip():
                        break
                        
                except:
                    continue
            
            if not content_html:
                # Fallback: get all text content
                try:
                    body = self.driver.find_element(By.TAG_NAME, 'body')
                    content_html = body.text
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
            # Remove Korean text and extract date
            date_match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        
        # Fallback to current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def crawl_all_posts(self, max_posts=20):
        """Crawl all posts"""
        post_links = self.get_post_links()
        
        if not post_links:
            print("No posts found!")
            return []
        
        # Limit number of posts
        post_links = post_links[:max_posts]
        
        all_posts = []
        
        for i, post_info in enumerate(post_links, 1):
            print(f"\n[{i}/{len(post_links)}] Processing: {post_info['title']}")
            
            post_data = self.crawl_post(post_info['url'], post_info['title'])
            
            if post_data:
                all_posts.append(post_data)
                print(f"✓ Successfully crawled: {post_data['title']}")
                if post_data['images']:
                    print(f"  Found {len(post_data['images'])} images")
            else:
                print(f"✗ Failed to crawl: {post_info['title']}")
            
            # Be respectful to the server
            time.sleep(2)
        
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
            "content": post['content'],  # Keep HTML formatting
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

def create_individual_posts(posts, output_dir="pages/blog/posts"):
    """Create individual HTML files for each post"""
    os.makedirs(output_dir, exist_ok=True)
    
    for post in posts:
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', post['title'])
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{post['date']}-{safe_title}.html"
        
        # Create HTML content with images and formatting
        category_html = f"<span> | 🏷️ {post['category']}</span>" if post['category'] else ""
        
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
    <meta name="description" content="{re.sub(r'<[^>]+>', '', post['content'])[:160]}">
    <link rel="stylesheet" href="../../styles.css">
    <style>
        body {{ 
            background: #0d0f17; 
            color: #fff; 
            font-family: 'Inter', sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 2rem;
            max-width: 900px;
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
        .post-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        .post-content p {{
            margin-bottom: 1rem;
        }}
        .post-content h1, .post-content h2, .post-content h3 {{
            color: #667eea;
            margin-top: 2rem;
            margin-bottom: 1rem;
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
    <a href="../blog.html" class="back-link">← Back to Blog</a>
    
    <div class="post-header">
        <div class="post-meta">
            <span>📅 {post['date']}</span>
            {category_html}
            <span> | 🔗 <a href="{post['original_url']}" target="_blank">Original Post</a></span>
        </div>
        <h1 class="post-title">{post['title']}</h1>
        {tags_html}
    </div>
    
    <div class="post-content">
        {post['content']}
    </div>
    
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
        <a href="../blog.html" class="back-link">← Back to Blog</a>
    </div>
</body>
</html>"""
        
        # Save file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Created: {filename}")

def main():
    print("🚀 Starting Advanced Tistory Crawler...")
    
    crawler = AdvancedTistoryCrawler()
    
    try:
        # Crawl posts
        posts = crawler.crawl_all_posts(max_posts=15)  # Start with 15 posts
        
        if posts:
            print(f"\n✅ Successfully crawled {len(posts)} posts!")
            
            # Save to JSON
            save_to_blog_format(posts)
            
            # Create individual HTML files
            create_individual_posts(posts)
            
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
