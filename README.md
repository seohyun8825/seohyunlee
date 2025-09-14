# Seohyun Portfolio (GitHub Pages, gh-pages branch)

Static site (HTML/CSS/JS). Deploys to GitHub Pages using the `gh-pages` npm package.

## Folder Structure
- `index.html`, `styles.css`, `script.js`, `.nojekyll`
- `src/images/*` (images)
- `src/media/*` (audio)

## One-time Setup
1) Create a repo (example: `seohyun-portfolio`) on GitHub.

2) In PowerShell, from this folder:
```
cd C:\Users\user\Desktop\booup\my_website
npm init -y        # if package.json not present (we already added one)
npm install --save-dev gh-pages
```

3) Push the source (optional but recommended):
```
git init -b main
git add .
git commit -m "Add portfolio site (gh-pages)"
git remote add origin https://github.com/<username>/seohyun-portfolio.git
git push -u origin main
```

## Deploy to gh-pages Branch
```
npm run deploy
```
- This creates/updates the `gh-pages` branch with the site files from the current directory (`-d .`).

## Enable GitHub Pages
- GitHub → repo → Settings → Pages
- Source: Deploy from a branch
- Branch: `gh-pages` • Folder: `/` → Save
- URL: `https://<username>.github.io/seohyun-portfolio/` (wait ~1–2 min)

## Notes
- All resource paths are relative (e.g., `src/images/...`), so Pages will resolve them correctly.
- `.nojekyll` ensures files are served as-is.
- To redeploy after changes, commit and run: `npm run deploy`.
