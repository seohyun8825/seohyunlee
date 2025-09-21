#!/usr/bin/env python3
"""
Update posts.json with new shortened filenames
"""

import json
import os
import re
from pathlib import Path

def update_filenames_after_rename(posts_json_path="pages/blog/posts.json", posts_dir="pages/blog/posts"):
    """Update posts.json with new shortened filenames"""
    
    print("Updating posts.json with new shortened filenames...")
    
    try:
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            posts = data.get('posts', [])
    except FileNotFoundError:
        print(f"Error: {posts_json_path} not found.")
        return
    
    # Get actual HTML filenames from the directory
    posts_path = Path(posts_dir)
    html_files = [f.name for f in posts_path.glob("*.html")]
    
    updated_posts = []
    for i, post in enumerate(posts):
        # Find matching HTML file by date and partial title match
        post_date = post['date']
        post_title = post['title'].replace(' — happy8825', '')
        
        # Try to find matching file
        found_filename = None
        for html_file in html_files:
            if html_file.startswith(post_date):
                # Extract title part from filename
                match = re.match(rf'{post_date}-(.+)-happy8825\.html', html_file)
                if match:
                    filename_title = match.group(1)
                    # Check if this looks like a shortened version of our title
                    if (filename_title.lower() in post_title.lower() or 
                        post_title.lower().split()[0].lower() in filename_title.lower()):
                        found_filename = html_file
                        break
        
        if found_filename:
            post['filename'] = found_filename
        else:
            # Fallback: generate filename from date and title
            safe_title = re.sub(r'[^\w\s-]', '', post_title)
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            if len(safe_title) > 47:
                safe_title = safe_title[:47] + "..."
            post['filename'] = f"{post_date}-{safe_title}-happy8825.html"
            print(f"Warning: Generated filename for '{post['title']}': {post['filename']}")
        
        updated_posts.append(post)
        print(f"[{i+1}/{len(posts)}] {post['title'][:50]}... -> {post['filename']}")

    data['posts'] = updated_posts
    
    with open(posts_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Successfully updated {len(posts)} posts with new filenames!")

if __name__ == "__main__":
    update_filenames_after_rename()
