🌐 **Website**: [seohyunleee.com](https://seohyunleee.com)

This is a personal blog website built with HTML, CSS, and JavaScript

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- Node.js and npm
- Git

### Installation
1. Clone the repository:
```bash
git clone https://github.com/seohyun8825/seohyunlee.git
cd seohyunlee
```

2. Install dependencies:
```bash
npm install
```

## 📝 Blog Post Management

### Adding New Posts

1. **Run the post creation script:**
```bash
python add_new_post.py
```

2. **Fill in the required information:**
```
📝 새로운 블로그 포스트 추가
========================================
포스트 제목을 입력하세요: Your Post Title
카테고리를 입력하세요 (예: Computer Vision, NLP, Robot): Computer Vision
태그를 쉼표로 구분해서 입력하세요 (예: DL, NLP, Vision): AI, Vision, Deep Learning
```

3. **Edit the generated HTML file:**
   - The script will create a new HTML file (e.g., `102.html`) in `pages/blog/posts/`
   - Open the file and edit the content in the `<div class="post-content">` section
   - You can use HTML tags or markdown-style formatting

4. **Deploy the changes:**
```bash
npm run publish
```

### Deleting Posts

1. **Run the post deletion script:**
```bash
python delete_post.py
```

2. **Enter the filename to delete:**
```
🗑️ 블로그 포스트 삭제
========================================
삭제할 포스트 파일명을 입력하세요 (예: 93.html): 93.html
```

3. **Confirm deletion:**
   - The script will show post details and ask for confirmation
   - Type `y` to confirm deletion

4. **Deploy the changes:**
```bash
npm run publish
```

## 🚀 Deployment

### Deploy to seohyunleee.com
```bash
npm run publish
```