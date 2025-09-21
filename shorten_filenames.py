#!/usr/bin/env python3
"""
Shorten HTML filenames to avoid Git long filename issues
"""

import os
import re
from pathlib import Path

def shorten_filenames(posts_dir="pages/blog/posts", max_length=80):
    """Shorten all filenames to be under max_length"""
    
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Directory {posts_dir} not found")
        return
    
    html_files = list(posts_path.glob("*.html"))
    renamed_count = 0
    
    for html_file in html_files:
        if len(html_file.name) > max_length:
            # Extract date and create much shorter name
            match = re.match(r'(\d{4}-\d{2}-\d{2})-([^-]+)', html_file.name)
            if match:
                date_part = match.group(1)
                title_part = match.group(2)
                
                # Take only first few words of title to make it very short
                words = title_part.split('-')
                if len(words) > 3:
                    short_title = '-'.join(words[:3])  # Take only first 3 words
                else:
                    short_title = title_part
                
                # Further shorten if still too long
                if len(short_title) > 30:
                    short_title = short_title[:27] + "..."
                
                new_name = f"{date_part}-{short_title}-happy8825.html"
                new_path = posts_path / new_name
                
                # Avoid conflicts by adding number if file exists
                counter = 1
                original_new_name = new_name
                while new_path.exists() and new_path != html_file:
                    name_without_ext = original_new_name.replace('.html', '')
                    new_name = f"{name_without_ext}-{counter}.html"
                    new_path = posts_path / new_name
                    counter += 1
                
                try:
                    html_file.rename(new_path)
                    print(f"Renamed: {html_file.name[:60]}... -> {new_name}")
                    renamed_count += 1
                except Exception as e:
                    print(f"Error renaming {html_file.name}: {e}")
            else:
                print(f"Could not parse filename: {html_file.name}")
    
    print(f"\n✅ Renamed {renamed_count} files to be under {max_length} characters")

if __name__ == "__main__":
    shorten_filenames()
