#!/usr/bin/env python3
"""
Update posts.json with correct filename mappings for individual HTML files
"""

import json
import os
import re
from pathlib import Path

def update_posts_with_filenames():
    # Load posts.json
    posts_json_path = "pages/blog/posts.json"
    with open(posts_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    posts = data.get('posts', [])
    posts_dir = Path("pages/blog/posts")
    
    # Get all HTML files
    html_files = list(posts_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files")
    
    # Create a mapping from URL number to filename
    url_to_filename = {}
    for html_file in html_files:
        filename = html_file.name
        # Try to extract URL number from the filename or content
        # For now, we'll create a simple mapping based on order
        pass
    
    # Update posts with filename field
    updated_posts = []
    for i, post in enumerate(posts):
        # Generate filename from date and title (remove existing -happy8825 suffix if present)
        title = post['title'].replace(' — happy8825', '').replace(' — happy8825', '')
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{post['date']}-{safe_title}-happy8825.html"
        
        # Add filename field
        post['filename'] = filename
        updated_posts.append(post)
        
        print(f"[{i+1}/{len(posts)}] {post['title'][:50]}... -> {filename}")
    
    # Save updated posts.json
    data['posts'] = updated_posts
    with open(posts_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Successfully updated {len(updated_posts)} posts with filename field!")

if __name__ == "__main__":
    update_posts_with_filenames()
