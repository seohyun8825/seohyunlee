#!/usr/bin/env python3
"""
posts.json에서 -happy8825 부분을 제거하는 스크립트
"""

import json
import os

def remove_happy8825_from_posts():
    """posts.json에서 -happy8825 부분을 제거"""
    
    print("🧹 Removing '-happy8825' from posts.json...")
    
    posts_json_path = "pages/blog/posts.json"
    
    try:
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            posts = data.get('posts', [])
    except FileNotFoundError:
        print(f"❌ Error: {posts_json_path} not found.")
        return
    
    updated_count = 0
    
    for post in posts:
        # URL에서 -happy8825 제거
        if 'url' in post and post['url'].endswith('-happy8825.html'):
            old_url = post['url']
            post['url'] = post['url'].replace('-happy8825.html', '.html')
            print(f"✅ Updated URL: {old_url} -> {post['url']}")
            updated_count += 1
        
        # 제목에서 -happy8825 제거
        if 'title' in post and ' — happy8825' in post['title']:
            old_title = post['title']
            post['title'] = post['title'].replace(' — happy8825', '')
            print(f"✅ Updated Title: {old_title} -> {post['title']}")
            updated_count += 1
        
        # excerpt에서도 제거
        if 'excerpt' in post and ' — happy8825' in post['excerpt']:
            old_excerpt = post['excerpt']
            post['excerpt'] = post['excerpt'].replace(' — happy8825', '')
            print(f"✅ Updated Excerpt: {old_excerpt} -> {post['excerpt']}")
            updated_count += 1
    
    # 업데이트된 데이터 저장
    data['posts'] = posts
    
    try:
        with open(posts_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 Successfully updated {updated_count} entries in posts.json!")
    except Exception as e:
        print(f"❌ Error updating posts.json: {e}")

if __name__ == "__main__":
    remove_happy8825_from_posts()
