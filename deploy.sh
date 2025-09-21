#!/bin/bash

# 자동 배포 스크립트
echo "🚀 Starting deployment process..."

# main 브랜치에 변경사항 푸시
echo "📤 Pushing to main branch..."
git add .
git commit -m "Auto update"
git push origin main

# gh-pages 브랜치로 이동
echo "🔄 Switching to gh-pages branch..."
git checkout gh-pages

# main 브랜치 내용을 gh-pages에 병합
echo "🔀 Merging main into gh-pages..."
git merge main

# gh-pages에 푸시 (사이트에 반영)
echo "🌐 Deploying to website..."
git push origin gh-pages

# main 브랜치로 돌아가기
echo "↩️ Returning to main branch..."
git checkout main

echo "✅ Deployment completed! Website updated at seohyunleee.com"
