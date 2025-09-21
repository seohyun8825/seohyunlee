#!/usr/bin/env python3
"""
Fix remaining filenames in posts.json for the files that were renamed to 93-101
"""

import json

def fix_remaining_filenames(posts_json_path="pages/blog/posts.json"):
    """Update the remaining files to their new numeric names"""
    
    # Mapping of old filenames to new numeric names
    filename_mapping = {
        "2024-06-29-MintNetcodeReview-Building-Invertible-Neural-Ne...-happy8825.html": "93.html",
        "2024-08-07-Linear-Equation-happy8825.html": "94.html",
        "2024-08-07-Linear-System-Identity-Matrix-happy8825.html": "95.html",
        "2024-09-03-Visual-Autoregressive-Modeling-happy8825.html": "96.html",
        "2024-11-05-LAMPLearn-A-Motion-Pattern-for-Few-Shot-Based-V...-happy8825.html": "97.html",
        "2025-01-31-Flow-matching-Guide-and-Code-Flow-model3탄-happy8825.html": "98.html",
        "2025-01-31-Flow-Matching-Guide-and-Code-Flow-models-2탄-happy8825.html": "99.html",
        "2025-03-02-ODPG-Outfitting-Diffusion-With-Pose-Guided-Cond...-happy8825.html": "100.html",
        "2025-03-25-Luxury한-인생을-살아가는법--happy8825.html": "101.html"
    }
    
    try:
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            posts = data.get('posts', [])
    except FileNotFoundError:
        print(f"Error: {posts_json_path} not found.")
        return
    
    updated_count = 0
    for post in posts:
        current_filename = post.get('filename', '')
        
        # Check if this filename needs to be updated
        for old_pattern, new_name in filename_mapping.items():
            if old_pattern in current_filename or current_filename in old_pattern:
                post['filename'] = new_name
                print(f"Updated: {current_filename[:50]}... -> {new_name}")
                updated_count += 1
                break
    
    # Save updated data
    data['posts'] = posts
    
    try:
        with open(posts_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Successfully updated {updated_count} filenames in posts.json!")
    except Exception as e:
        print(f"Error updating posts.json: {e}")

if __name__ == "__main__":
    fix_remaining_filenames()
