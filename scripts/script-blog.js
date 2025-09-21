// Blog functionality
let blogData = null;
let currentFilter = 'all';

// Load blog data and initialize
async function loadBlogData() {
  try {
    const response = await fetch('./blog/posts.json');
    blogData = await response.json();
    initializeBlog();
  } catch (error) {
    console.error('Failed to load blog data:', error);
  }
}

function initializeBlog() {
  if (!blogData) return;
  
  renderCategories();
  renderTags();
  renderPosts();
  setupFilters();
}

function renderCategories() {
  const categoryList = document.getElementById('category-list');
  if (!categoryList || !blogData.categories) return;
  
  categoryList.innerHTML = blogData.categories.map(category => `
    <li class="category-item">
      <a href="#" data-category="${category.name}" class="category-link">
        <span>${category.name}</span>
        <span class="category-count">${category.count}</span>
      </a>
    </li>
  `).join('');
  
  // Add click handlers
  categoryList.addEventListener('click', (e) => {
    if (e.target.closest('.category-link')) {
      e.preventDefault();
      const category = e.target.closest('.category-link').dataset.category;
      filterByCategory(category);
    }
  });
}

function renderTags() {
  const tagList = document.getElementById('tag-list');
  if (!tagList || !blogData.tags) return;
  
  // Sort tags by count and take top 10
  const topTags = blogData.tags
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
  
  tagList.innerHTML = topTags.map(tag => `
    <li class="tag-item">
      <a href="#" data-tag="${tag.name}" class="tag-link">
        <span>${tag.name}</span>
        <span class="tag-count">${tag.count}</span>
      </a>
    </li>
  `).join('');
  
  // Add click handlers
  tagList.addEventListener('click', (e) => {
    if (e.target.closest('.tag-link')) {
      e.preventDefault();
      const tag = e.target.closest('.tag-link').dataset.tag;
      filterByTag(tag);
    }
  });
}

function renderPosts(filteredPosts = null) {
  const postsContainer = document.getElementById('blog-posts');
  if (!postsContainer || !blogData.posts) return;
  
  let posts = filteredPosts || [...blogData.posts];
  
  // Sort posts by date (newest first)
  posts = posts.sort((a, b) => {
    const dateA = new Date(a.date);
    const dateB = new Date(b.date);
    return dateB - dateA; // Newest first
  });
  
  postsContainer.innerHTML = posts.map(post => `
    <article class="blog-post">
      <div class="post-meta">
        <span class="post-date">${formatDate(post.date)}</span>
        <span class="post-category">${post.category}</span>
      </div>
      <h2 class="post-title">${post.title}</h2>
      <div class="post-tags">
        ${post.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
      </div>
      <p class="post-excerpt">${post.excerpt}</p>
      <a href="#" class="read-more" data-post-id="${post.id}">
        Read More
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </a>
    </article>
  `).join('');
  
  // Add click handlers for read more
  postsContainer.addEventListener('click', (e) => {
    if (e.target.closest('.read-more')) {
      e.preventDefault();
      const postId = e.target.closest('.read-more').dataset.postId;
      // Find the post data to get filename
      const post = blogData.posts.find(p => p.id === postId);
      if (post && post.filename) {
        // Navigate to individual post HTML file using the filename field
        window.location.href = `./blog/posts/${post.filename}`;
      }
    }
  });
}

function setupFilters() {
  const filterButtons = document.querySelectorAll('.filter-btn');
  
  filterButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      // Update active state
      filterButtons.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      
      // Filter posts
      const filter = e.target.dataset.filter;
      currentFilter = filter;
      
      if (filter === 'all') {
        renderPosts();
      } else {
        // More flexible category matching
        const filteredPosts = [...blogData.posts].filter(post => {
          if (!post.category) return false;
          
          // Direct match
          if (post.category === filter) return true;
          
          // Partial match for "Computer Vision"
          if (filter === 'Computer Vision' && post.category.includes('Computer Vision')) return true;
          
          // Partial match for "NLP"
          if (filter === 'NLP' && post.category.includes('NLP')) return true;
          
          // Partial match for "Robot" (case insensitive)
          if (filter === 'Robot' && post.category.toLowerCase().includes('robot')) return true;
          
          return false;
        });
        renderPosts(filteredPosts);
      }
    });
  });
}

function filterByCategory(category) {
  // Update filter buttons
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(b => b.classList.remove('active'));
  
  // Map category names to filter buttons
  let filterValue = category;
  if (category.includes('Computer Vision')) {
    filterValue = 'Computer Vision';
  } else if (category.includes('NLP')) {
    filterValue = 'NLP';
  } else if (category.includes('Robot')) {
    filterValue = 'Robot';
  }
  
  const categoryBtn = document.querySelector(`[data-filter="${filterValue}"]`);
  if (categoryBtn) {
    categoryBtn.classList.add('active');
  } else {
    document.querySelector('[data-filter="all"]').classList.add('active');
  }
  
  // Filter posts with flexible matching
  const filteredPosts = [...blogData.posts].filter(post => {
    if (!post.category) return false;
    
    // Direct match
    if (post.category === category) return true;
    
    // Partial match for "Computer Vision"
    if (filterValue === 'Computer Vision' && post.category.includes('Computer Vision')) return true;
    
    // Partial match for "NLP"
    if (filterValue === 'NLP' && post.category.includes('NLP')) return true;
    
    // Partial match for "Robot" (case insensitive)
    if (filterValue === 'Robot' && post.category.toLowerCase().includes('robot')) return true;
    
    return false;
  });
  renderPosts(filteredPosts);
  currentFilter = filterValue;
}

function filterByTag(tag) {
  // Filter posts by tag
  const filteredPosts = [...blogData.posts].filter(post => post.tags.includes(tag));
  renderPosts(filteredPosts);
  
  // Update filter buttons
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(b => b.classList.remove('active'));
  document.querySelector('[data-filter="all"]').classList.add('active');
  currentFilter = 'all';
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

// Initialize blog when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('/blog')) {
    loadBlogData();
  }
});

// Background Audio System
(function() {
  const audio = new Audio("../src/media/luxury.mp3");
  let enabled = false;
  let startOffset = 0;

  const FADE_MS = 1500;
  const DEFAULT_VOLUME = 0.2;

  let fadeTimeoutId = null;

  function cancelFade() {
    if (fadeTimeoutId) {
      clearTimeout(fadeTimeoutId);
      fadeTimeoutId = null;
    }
  }

  function fadeTo(targetVolume, fadeMs) {
    cancelFade(); // Cancel any existing fade
    const currentVolume = audio.volume;
    const steps = 20;
    const stepSize = (targetVolume - currentVolume) / steps;
    const stepMs = fadeMs / steps;

    let currentStep = 0;

    function step() {
      currentStep++;
      audio.volume = Math.min(1, Math.max(0, currentVolume + stepSize * currentStep));
      
      if (currentStep < steps) {
        fadeTimeoutId = setTimeout(step, stepMs);
      } else {
        fadeTimeoutId = null;
      }
    }

    step();
  }

  function ensureStartOffset() {
    if (startOffset === 0) {
      audio.currentTime = startOffset;
    }
  }

  function applyState() {
    if (enabled && !audio.muted) {
      ensureStartOffset();
      audio.play().catch(() => {
        enabled = false;
        updateUI();
      });
    } else {
      audio.pause();
    }
    updateUI();
  }

  function updateUI() {
    const toggle = document.getElementById('music-toggle');
    if (toggle) {
      toggle.textContent = enabled ? '🎵' : '🔇';
      toggle.title = enabled ? 'Disable background music' : 'Enable background music';
    }
  }

  window.addEventListener('beforeunload', () => {
    audio.pause();
  });

  audio.addEventListener('ended', () => {
    if (enabled) {
      audio.currentTime = startOffset;
      audio.play();
    }
  });

  // Loop setup
  audio.loop = true;
  audio.volume = DEFAULT_VOLUME;
  audio.muted = true; // keep muted until user clicks
  applyState();

  const toggle = document.getElementById('music-toggle');
  if (toggle) {
    toggle.addEventListener('click', async () => {
      enabled = !enabled;
      if (enabled) {
        ensureStartOffset(); // will set to 0
        audio.muted = false;
        audio.volume = 0;
        try {
          await audio.play();
          fadeTo(DEFAULT_VOLUME, FADE_MS);
        } catch (_) {
          // If playback fails, revert UI state
          enabled = false;
        }
      } else {
        cancelFade();
        audio.pause();
        audio.muted = true;
      }
      updateUI();
    });
  }

  // Remove global gesture-based auto-start; playback only starts via the toggle click
})();