#!/usr/bin/env python3
"""
Manual crawl of specific Tistory posts based on web search results
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

class ManualTistoryCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def parse_korean_date(self, date_text):
        """Parse Korean date format to YYYY-MM-DD"""
        try:
            # Remove Korean text and extract date
            date_match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        
        # Fallback to current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def crawl_post(self, url, title, date, category, tags=None):
        """Crawl a specific post"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract content - try different selectors
            content = ""
            content_selectors = [
                'div.entry-content',
                'div.post-content', 
                'div.content',
                'article',
                'div.tt_article_useless_p_margin'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style tags
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    content = content_elem.get_text().strip()
                    break
            
            if not content:
                # Fallback: get all text from body
                body = soup.find('body')
                if body:
                    for script in body(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                    content = body.get_text().strip()
            
            return {
                'title': title,
                'date': date,
                'category': category,
                'content': content,
                'tags': tags or [],
                'url': url,
                'html': html
            }
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None

def main():
    # Based on web search results, create posts manually
    posts_data = [
        {
            'title': 'Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware',
            'date': '2025-09-15',
            'category': 'Robot',
            'tags': ['ACT', 'Imitation Learning', 'Robotics', 'CVAE'],
            'content': '''ACT, Architecture of Action Chunking with Transformers
ACT란, imitation learning 알고리즘으로 fine grain하게 로봇을 조종하기 위한 알고리즘이다. 집에 로봇을 조립한 기념으로 읽어봤다. 처음 접하는 분야라 뭐부터 읽어야할지 모르겠어서 추천을 받아왔다. 최근까지도 가장 많이 쓰이는 방식이라고한다.

참 흥미로운 로봇세상이다 느리지만 RTX 4050에서 vla 학습이랑 inference 다 잘돌아간다 single step을 predict하는 대신에 chunks of action을 예측한다는게 핵심 아이디어이다. Conditional Variational Autoenncoder , CVAE를 transformer로 만든 구조이다.

현재 joint space에서 action을 예측하는데, 이게 로봇의 물리적 제약과 맞지 않을 수 있다. 그래서 ACT는 action chunking을 통해 더 자연스러운 로봇 제어를 가능하게 한다.'''
        },
        {
            'title': 'Concept-skill Transferability-based Data Selection for Large Vision-Language Models',
            'date': '2025-08-16',
            'category': 'Computer Vision',
            'tags': ['VLM', 'Data Selection', 'Clustering', 'Training Efficiency'],
            'content': '''Intro
데이터셋이 너무 큰 경우 학습 비용이 너무 많이 든다. 그래서 좋은 데이터만 어떻게 잘 뽑아 쓸까, 에 대한 연구이다.

핵심 아이디어는 작은 vlm 을 사용해서, 어떤 데이터가 유용할지 골라낸다. 작은 모델의 내부 representation을 이용해서 training 데이터를 클러스터링을 한다. 그래서 데이터 속에서 concept - skill composition을 파악한다. (street sign/OCR) 이런식으로 어떤 컨셉인지, 그리고 이걸 답하기 위해서는 어떤 skill 이 필요한지 이런식으로 조합하는 느낌인거같다.

이렇게 하면 다양한 데이터를 소량만 뽑아도 성능 유지가 가능하다. 그래서 concept-skill composition으로 클러스터링을 해놓고, 각 클러스터에서 density를 계산해서 대표적인 샘플들을 선택한다.'''
        },
        {
            'title': 'Log-Linear Attention 빠른 트랜스포머!?',
            'date': '2025-06-27',
            'category': 'Computer Vision',
            'tags': ['Transformer', 'Attention', 'Long Context', 'Efficiency'],
            'content': '''long context를 어떻게 처리할지, AI에서는 굉장히 중요한 문제이다. Transformer,, 굉장하지만 단점이 너무나도 명확하다. 바로 quadratic-compute 이다.

어디서 bottleneck이 발생하냐면, transformer의 selfattention 그림인데, attention matrix부분을 보자. attention matrix이 n^2 이 되는데, 그럼 number of token이 많아지면 n^2배만큼 quadratic하게 늘어나게 될것이다.

Log-Linear Attention은 이 문제를 해결하기 위해 attention 계산을 log-linear complexity로 줄이는 방법이다. 기존의 softmax attention 대신 log-space에서 계산을 수행하여 메모리와 계산 효율성을 크게 향상시킨다.'''
        },
        {
            'title': 'ReVisionLLM: Recursive Vision-Language Model for Temporal Grounding in Hour-Long Videos',
            'date': '2025-05-31',
            'category': 'Computer Vision',
            'tags': ['VLM', 'Video Understanding', 'Temporal Grounding', 'Recursive'],
            'content': '''긴 영상에서 '언제, 어떤 일이 일어났는지'를 찾아내는 것을 기존 VLM은 잘 못한다. 프레임 수 한계 때문에 중요한 순간이 누락되기 쉽고, 결과적으로 시간 경계가 흐릿해진다.

ReVisionLLM은 이 한계를 극복하기 위해 인간이 영상을 훑는 방식을 모방해서 재귀적 탐색 방식을 사용한다. 모델은 먼저 저해상도 전체 scan으로 관심 구간을 대략적으로 지정한다. 이후 해당 구간만 프레임 해상도를 높여 다시 분석하고, 필요하면 더 세밀하게 확대한다.

이렇게 "넓게 → 좁게 → 더 좁게" 과정을 반복하며 최종적으로 초 단위 경계를 산출한다. 훈련 과정도 hierarchical 하게 설계한다. 짧은 10–30 초 클립에 먼저 사건 인지 능력을 학습시킨 뒤, 점차 길이를 늘려 몇 시간짜리 영상까지 확장 학습을 진행한다.'''
        },
        {
            'title': 'DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models',
            'date': '2025-04-27',
            'category': 'NLP',
            'tags': ['Math', 'Reasoning', 'Data Quality', 'GRPO'],
            'content': '''조금 오래된.. 작년 초 논문이긴 하지만, 특정 Task 에서 Sota를 달성하기 위해 어떤 방법을 사용했고, 특히 부족한 데이터셋은 어떻게 해결했는지 궁금해서 읽어봤다.

우선 DeepSeekMath는 수학 벤치마크에서 당시 Sota를 달성했다. 두가지 접근법이 있었는데 아주아주 많은 고품질의 데이터셋을 모은것, 그리고 GRPO 이다.

먼저 아주아주 많은 고품질의 데이터셋은 어떻게 모았을까. 알다시피 데이터셋을 만드는건 돈이 많이 든다. GPT를 태워서 데이터셋을 만들다보면 순식간에 몇백이 나가있을거다.. 여기서 소개한 데이터셋 모으기 파이프라인의 주요 아이디어는, 데이터를 제작하는게 아니고, 이미 있는 데이터셋을 잘 걸러내서 필요한것들을 잘 뽑아내보자 이다.'''
        }
    ]
    
    # Convert to blog format
    blog_data = {
        "posts": [],
        "categories": {},
        "tags": {}
    }
    
    for i, post_data in enumerate(posts_data):
        post_id = f"post-{i+1}"
        
        # Clean content for excerpt
        content = post_data['content']
        excerpt = content[:200] + "..." if len(content) > 200 else content
        
        blog_post = {
            "id": post_id,
            "title": post_data['title'],
            "date": post_data['date'],
            "category": post_data['category'],
            "tags": post_data['tags'],
            "excerpt": excerpt,
            "content": content,
            "original_url": f"https://happy8825.tistory.com/entry/{i+1}"
        }
        
        blog_data["posts"].append(blog_post)
        
        # Count categories
        category = post_data['category']
        if category not in blog_data["categories"]:
            blog_data["categories"][category] = 0
        blog_data["categories"][category] += 1
        
        # Count tags
        for tag in post_data['tags']:
            if tag not in blog_data["tags"]:
                blog_data["tags"][tag] = 0
            blog_data["tags"][tag] += 1
    
    # Convert counts to arrays for frontend
    blog_data["categories"] = [
        {"name": name, "count": count, "color": "#667eea"} 
        for name, count in blog_data["categories"].items()
    ]
    blog_data["tags"] = [
        {"name": name, "count": count} 
        for name, count in blog_data["tags"].items()
    ]
    
    # Save to file
    os.makedirs("pages/blog", exist_ok=True)
    with open("pages/blog/posts.json", 'w', encoding='utf-8') as f:
        json.dump(blog_data, f, ensure_ascii=False, indent=2)
    
    print(f"Created {len(posts_data)} posts from manual data")
    print("Saved to pages/blog/posts.json")
    
    # Create individual HTML files
    os.makedirs("pages/blog/posts", exist_ok=True)
    
    for post_data in posts_data:
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', post_data['title'])
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{post_data['date']}-{safe_title}.html"
        
        # Create HTML content
        back_arrow = "←"
        
        category_html = f"<span> | 🏷️ {post_data['category']}</span>" if post_data['category'] else ""
        
        tags_html = ""
        if post_data['tags']:
            tag_spans = [f'<span style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 12px; margin-right: 0.5rem; font-size: 0.9rem;">#{tag}</span>' for tag in post_data['tags']]
            tags_html = f"<div class='tags'>{''.join(tag_spans)}</div>"
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_data['title']} - Seohyun Lee Blog</title>
    <meta name="description" content="{excerpt[:160]}">
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
    <a href="../blog.html" class="back-link">{back_arrow} Back to Blog</a>
    
    <div class="post-header">
        <div class="post-meta">
            <span>📅 {post_data['date']}</span>
            {category_html}
            <span> | 🔗 <a href="https://happy8825.tistory.com" target="_blank">Original Tistory</a></span>
        </div>
        <h1 class="post-title">{post_data['title']}</h1>
        {tags_html}
    </div>
    
    <div class="post-content">
{post_data['content']}
    </div>
    
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
        <a href="../blog.html" class="back-link">{back_arrow} Back to Blog</a>
    </div>
</body>
</html>"""
        
        # Save file
        filepath = os.path.join("pages/blog/posts", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Created: {filename}")

if __name__ == "__main__":
    main()
