#!/usr/bin/env python3
"""
새로운 블로그 포스트를 쉽게 추가하는 스크립트
"""

import json
import os
from datetime import datetime

def add_new_post():
    """새로운 포스트를 추가하는 함수"""
    
    print("📝 새로운 블로그 포스트 추가")
    print("=" * 40)
    
    # 사용자 입력 받기
    title = input("포스트 제목을 입력하세요: ")
    category = input("카테고리를 입력하세요 (예: Computer Vision, NLP, Robot): ")
    tags_input = input("태그를 쉼표로 구분해서 입력하세요 (예: DL, NLP, Vision): ")
    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    
    # 현재 날짜 사용
    date = datetime.now().strftime("%Y-%m-%d")
    
    # 다음 번호 찾기
    posts_dir = "pages/blog/posts"
    existing_files = [f for f in os.listdir(posts_dir) if f.endswith('.html')]
    next_number = len(existing_files) + 1
    
    # 새 HTML 파일명
    new_filename = f"{next_number}.html"
    
    print(f"\n📄 새 포스트 정보:")
    print(f"   제목: {title}")
    print(f"   카테고리: {category}")
    print(f"   태그: {', '.join(tags)}")
    print(f"   파일명: {new_filename}")
    print(f"   날짜: {date}")
    
    # HTML 템플릿
    html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Seohyun Lee Blog</title>
    <meta name="description" content="{title}">
    <link rel="stylesheet" href="../../styles.css">
    <style>
        body {{ 
            background: #0d0f17; 
            color: #fff; 
            font-family: 'Inter', sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 2rem;
            max-width: 800px;
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
            white-space: pre-wrap;
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
    <a href="../../blog.html" class="back-link">← Back to Blog</a>
    
    <div class="post-header">
        <div class="post-meta">
            <span>📅 {date}</span>
            <span> | 🏷️ {category}</span>
        </div>
        <h1 class="post-title">{title}</h1>
        <div class='tags'>
            {''.join([f'<span style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 12px; margin-right: 0.5rem; font-size: 0.9rem;">#{tag}</span>' for tag in tags])}
        </div>
    </div>
    
    <div class="post-content">
여기에 포스트 내용을 작성하세요.

마크다운 형식으로 작성하거나 HTML 태그를 사용할 수 있습니다.

예시:
- **굵은 글씨**
- *기울임*
- [링크](URL)

코드 블록:
```python
def hello():
    print("Hello, World!")
```
    </div>
    
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
        <a href="../../blog.html" class="back-link">← Back to Blog</a>
    </div>
</body>
</html>"""
    
    # HTML 파일 생성
    html_path = os.path.join(posts_dir, new_filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ HTML 파일 생성: {html_path}")
    
    # posts.json 업데이트
    posts_json_path = "pages/blog/posts.json"
    
    try:
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"posts": []}
    
    # 새 포스트 정보
    new_post = {
        "id": f"post-{next_number}",
        "title": title,
        "date": date,
        "category": category,
        "tags": tags,
        "excerpt": title[:100] + "..." if len(title) > 100 else title,
        "content": f"<p>여기에 포스트 내용을 작성하세요.</p>",
        "images": [],
        "original_url": "",
        "filename": new_filename
    }
    
    # 새 포스트를 맨 앞에 추가 (최신 순으로)
    data["posts"].insert(0, new_post)
    
    # 파일 저장
    with open(posts_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ posts.json 업데이트 완료")
    
    print(f"\n🎉 새 포스트가 추가되었습니다!")
    print(f"📝 {html_path} 파일을 열어서 내용을 작성하세요.")
    print(f"🚀 내용 작성 후 'npm run publish'로 배포하세요.")

if __name__ == "__main__":
    add_new_post()
