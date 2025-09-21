#!/usr/bin/env python3
"""
Google Analytics를 웹사이트에 추가하는 스크립트
"""

import os

def add_google_analytics(tracking_id):
    """Google Analytics 추적 코드를 HTML 파일들에 추가"""
    
    # Google Analytics 코드
    analytics_code = f"""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={tracking_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{tracking_id}');
    </script>
    <!-- End Google Analytics -->
    """
    
    # HTML 파일들 목록
    html_files = [
        'index.html',
        'pages/blog.html',
        'pages/experience.html',
        'pages/awards.html',
        'pages/publications.html'
    ]
    
    # 각 HTML 파일에 Analytics 코드 추가
    for html_file in html_files:
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # </head> 태그 앞에 Analytics 코드 삽입
            if '</head>' in content and 'gtag' not in content:
                content = content.replace('</head>', f'{analytics_code}\n</head>')
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Analytics added to {html_file}")
            else:
                print(f"⚠️ {html_file} already has analytics or </head> not found")
    
    # 블로그 포스트들에도 추가
    posts_dir = 'pages/blog/posts'
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(posts_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '</head>' in content and 'gtag' not in content:
                    content = content.replace('</head>', f'{analytics_code}\n</head>')
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Analytics added to {filename}")
    
    print(f"\n🎉 Google Analytics ({tracking_id}) has been added to all HTML files!")
    print("📊 Visit https://analytics.google.com to view your website statistics")

if __name__ == "__main__":
    print("📊 Google Analytics Setup")
    print("=" * 40)
    print("1. Go to https://analytics.google.com")
    print("2. Create a new property for your website")
    print("3. Get your Tracking ID (format: G-XXXXXXXXXX)")
    print()
    
    tracking_id = input("Enter your Google Analytics Tracking ID: ")
    
    if tracking_id:
        add_google_analytics(tracking_id)
    else:
        print("❌ No tracking ID provided")
