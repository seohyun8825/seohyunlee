#!/usr/bin/env python3
"""
Create individual HTML files from the crawled blog posts
"""

import json
import os
import re

def create_individual_posts():
    # Load the crawled posts
    with open('pages/blog/posts.json', 'r', encoding='utf-8') as f:
        blog_data = json.load(f)
    
    posts = blog_data['posts']
    output_dir = "pages/blog/posts"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating {len(posts)} individual HTML files...")
    
    for i, post in enumerate(posts, 1):
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
        
        # Count images
        image_count = len(post.get('images', []))
        image_info = f" ({image_count} images)" if image_count > 0 else ""
        
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
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        .post-content p {{
            margin-bottom: 1rem;
        }}
        .post-content h1, .post-content h2, .post-content h3 {{
            color: #667eea;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        .post-content blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 1rem;
            margin: 1.5rem 0;
            color: #ccc;
            font-style: italic;
        }}
        .post-content code {{
            background: rgba(255, 255, 255, 0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}
        .post-content pre {{
            background: rgba(0, 0, 0, 0.3);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
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
            <span> | 📊 {image_count} images</span>
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
        
        print(f"[{i}/{len(posts)}] Created: {filename}{image_info}")
    
    print(f"\n✅ Successfully created {len(posts)} individual HTML files!")

if __name__ == "__main__":
    create_individual_posts()
