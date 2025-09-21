@echo off
echo 🚀 Starting deployment process...

echo 📤 Pushing to main branch...
git add .
git commit -m "Auto update"
git push origin main

echo 🔄 Switching to gh-pages branch...
git checkout gh-pages

echo 🔀 Merging main into gh-pages...
git merge main

echo 🌐 Deploying to website...
git push origin gh-pages

echo ↩️ Returning to main branch...
git checkout main

echo ✅ Deployment completed! Website updated at seohyunleee.com
pause
