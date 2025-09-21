#!/usr/bin/env python3
"""
Fix back links in individual blog post HTML files
"""

import os
import re
from pathlib import Path

def fix_back_links():
    posts_dir = Path("pages/blog/posts")
    html_files = list(posts_dir.glob("*.html"))
    
    print(f"Found {len(html_files)} HTML files to fix")
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the back link paths
            # From: href="../blog.html" 
            # To: href="../blog.html"
            old_link = 'href="../blog.html"'
            new_link = 'href="../blog.html"'
            
            if old_link in content:
                content = content.replace(old_link, new_link)
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Fixed: {html_file.name}")
            else:
                print(f"No back link found in: {html_file.name}")
                
        except Exception as e:
            print(f"Error processing {html_file.name}: {e}")
    
    print("\n✅ Back link fixing completed!")

if __name__ == "__main__":
    fix_back_links()
