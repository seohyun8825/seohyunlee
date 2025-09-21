#!/usr/bin/env python3
"""
블로그 포스트를 삭제하는 스크립트
"""

import json
import os

def delete_post():
    """포스트를 삭제하는 함수"""
    
    print("🗑️ 블로그 포스트 삭제")
    print("=" * 40)
    
    # 삭제할 파일명 입력 받기
    filename = input("삭제할 포스트 파일명을 입력하세요 (예: 93.html): ")
    
    # 파일 경로
    posts_dir = "pages/blog/posts"
    file_path = os.path.join(posts_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return
    
    # posts.json에서 해당 포스트 정보 찾기
    posts_json_path = "pages/blog/posts.json"
    
    try:
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            posts = data.get('posts', [])
    except FileNotFoundError:
        print(f"❌ {posts_json_path} 파일을 찾을 수 없습니다.")
        return
    
    # 해당 포스트 찾기
    post_to_delete = None
    for post in posts:
        if post.get('filename') == filename:
            post_to_delete = post
            break
    
    if not post_to_delete:
        print(f"❌ posts.json에서 해당 포스트를 찾을 수 없습니다: {filename}")
        return
    
    print(f"\n📄 삭제할 포스트 정보:")
    print(f"   제목: {post_to_delete.get('title', 'N/A')}")
    print(f"   날짜: {post_to_delete.get('date', 'N/A')}")
    print(f"   카테고리: {post_to_delete.get('category', 'N/A')}")
    print(f"   파일명: {filename}")
    
    # 확인
    confirm = input(f"\n정말로 '{post_to_delete.get('title', filename)}' 포스트를 삭제하시겠습니까? (y/N): ")
    
    if confirm.lower() != 'y':
        print("❌ 삭제가 취소되었습니다.")
        return
    
    # HTML 파일 삭제
    try:
        os.remove(file_path)
        print(f"✅ HTML 파일 삭제: {file_path}")
    except Exception as e:
        print(f"❌ HTML 파일 삭제 실패: {e}")
        return
    
    # posts.json에서 포스트 제거
    posts.remove(post_to_delete)
    data['posts'] = posts
    
    try:
        with open(posts_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ posts.json에서 포스트 정보 제거 완료")
    except Exception as e:
        print(f"❌ posts.json 업데이트 실패: {e}")
        return
    
    print(f"\n🎉 포스트가 성공적으로 삭제되었습니다!")
    print(f"🚀 'npm run publish'로 변경사항을 배포하세요.")

if __name__ == "__main__":
    delete_post()
