#!/usr/bin/env python3
"""
Rename HTML files to simple numbers (1.html, 2.html, etc.)
"""

import os
import json
from pathlib import Path

def rename_to_numbers(posts_json_path="pages/blog/posts.json", posts_dir="pages/blog/posts"):
    """Rename all HTML files to simple numbers"""
    
    # Load posts data to maintain order
    try:
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            posts = data.get('posts', [])
    except FileNotFoundError:
        print(f"Error: {posts_json_path} not found.")
        return
    
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Directory {posts_dir} not found")
        return
    
    # Get all HTML files
    html_files = list(posts_path.glob("*.html"))
    print(f"Found {len(html_files)} HTML files")
    
    # Create mapping from old filename to new number
    filename_mapping = {}
    
    # Sort posts by date (newest first) to maintain chronological order
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)
    
    for i, post in enumerate(sorted_posts, 1):
        old_filename = post.get('filename', '')
        if old_filename:
            old_path = posts_path / old_filename
            if old_path.exists():
                new_filename = f"{i}.html"
                filename_mapping[old_filename] = new_filename
                post['filename'] = new_filename
                print(f"[{i:2d}] {old_filename[:50]}... -> {new_filename}")
            else:
                print(f"Warning: File not found: {old_filename}")
    
    # Actually rename the files
    renamed_count = 0
    for old_filename, new_filename in filename_mapping.items():
        old_path = posts_path / old_filename
        new_path = posts_path / new_filename
        
        try:
            old_path.rename(new_path)
            renamed_count += 1
        except Exception as e:
            print(f"Error renaming {old_filename} to {new_filename}: {e}")
    
    # Update posts.json with new filenames
    data['posts'] = sorted_posts
    
    try:
        with open(posts_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Successfully renamed {renamed_count} files and updated posts.json!")
    except Exception as e:
        print(f"Error updating posts.json: {e}")

if __name__ == "__main__":
    rename_to_numbers()
