#!/usr/bin/env python3
"""
Rename HTML files with long names to shorter names
"""

import os
import re
from pathlib import Path

def rename_long_files(posts_dir="pages/blog/posts", max_length=100):
    """Rename files with names longer than max_length"""
    
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Directory {posts_dir} not found")
        return
    
    html_files = list(posts_path.glob("*.html"))
    renamed_count = 0
    
    for html_file in html_files:
        if len(html_file.name) > max_length:
            # Extract date and create shorter name
            match = re.match(r'(\d{4}-\d{2}-\d{2})-([^-]+)', html_file.name)
            if match:
                date_part = match.group(1)
                title_part = match.group(2)
                
                # Shorten title part
                if len(title_part) > 50:
                    title_part = title_part[:47] + "..."
                
                new_name = f"{date_part}-{title_part}-happy8825.html"
                new_path = posts_path / new_name
                
                try:
                    html_file.rename(new_path)
                    print(f"Renamed: {html_file.name} -> {new_name}")
                    renamed_count += 1
                except Exception as e:
                    print(f"Error renaming {html_file.name}: {e}")
            else:
                print(f"Could not parse filename: {html_file.name}")
    
    print(f"\n✅ Renamed {renamed_count} files")

if __name__ == "__main__":
    rename_long_files()
