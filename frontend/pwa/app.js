// PWA Application Logic
let cachedDataset = [];
let deferredPrompt;

// Initialization
document.addEventListener('DOMContentLoaded', initApp);
window.addEventListener('online', updateConnectionStatus);
window.addEventListener('offline', updateConnectionStatus);

document.getElementById('ask-btn').addEventListener('click', askQuestion);
document.getElementById('question-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    askQuestion();
  }
});
document.getElementById('sync-btn').addEventListener('click', syncDataset);
window.addEventListener('beforeinstallprompt', handleInstallPrompt);

async function initApp() {
  if ('serviceWorker' in navigator) {
    try {
      // Register service worker with correct scope
      const reg = await navigator.serviceWorker.register('/frontend/pwa/sw.js', {scope: '/frontend/pwa/'});
      console.log("[PWA] Service Worker registered with scope:", reg.scope);
    } catch (e) {
      console.log("[PWA] SW registration failed, running online-only:", e);
    }
  }

  // Load dataset from cache or network
  await loadDataset();
  
  // Update UI status
  await updateConnectionStatus();
}

async function loadDataset() {
  try {
    const response = await fetch('/data/edge_dataset.json');
    if (response.ok) {
      cachedDataset = await response.json();
      document.getElementById('dataset-status').textContent = `Dataset cached: ${cachedDataset.length} questions`;
    } else {
      console.log("[PWA] Failed to load dataset from network");
    }
  } catch (e) {
    console.log("[PWA] Network error loading dataset, may be offline");
  }
}

async function updateConnectionStatus() {
  const badge = document.getElementById('connection-badge');
  const edgeStatus = document.getElementById('edge-model-status');
  
  if (navigator.onLine) {
    try {
      const response = await fetch('/edge/health');
      if (response.ok) {
        badge.textContent = 'ONLINE';
        badge.className = 'badge online';
        edgeStatus.textContent = 'Edge model: Connected';
      } else {
        badge.textContent = 'ONLINE (No Edge)';
        badge.className = 'badge edge';
        edgeStatus.textContent = 'Edge model: Disconnected';
      }
    } catch (e) {
      badge.textContent = 'ONLINE (No Edge)';
      badge.className = 'badge edge';
      edgeStatus.textContent = 'Edge model: Disconnected';
    }
  } else {
    if (cachedDataset.length > 0) {
      badge.textContent = 'EDGE MODE';
      badge.className = 'badge edge';
    } else {
      badge.textContent = 'OFFLINE';
      badge.className = 'badge offline';
    }
    edgeStatus.textContent = 'Edge model: Offline';
  }
}

async function askQuestion() {
  const input = document.getElementById('question-input').value.trim();
  if (!input) {
    showToast("Please describe your emergency", "error");
    return;
  }

  document.getElementById('loading-spinner').style.display = 'block';
  document.getElementById('answer-area').style.display = 'none';

  let answer = "";
  let source = "";

  if (navigator.onLine) {
    try {
      const response = await fetch('/edge/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      });
      
      if (response.ok) {
        const data = await response.json();
        answer = data.answer;
        source = `Source: Edge AI (${data.source})`;
      } else {
        throw new Error("Edge endpoint failed");
      }
    } catch (e) {
      console.log("[PWA] Edge query failed, falling back to cache", e);
      const match = searchCachedDataset(input);
      if (match) {
        answer = match.answer;
        source = "Source: Cached Guide (fallback)";
      } else {
        answer = "No cached guidance matches. Call 119 for immediate help.";
        source = "Source: Offline Fallback";
      }
    }
  } else {
    const match = searchCachedDataset(input);
    if (match) {
      answer = match.answer;
      source = "Source: Cached Guide (offline)";
    } else {
      answer = "No cached guidance matches. Call 119 for immediate help.";
      source = "Source: Offline Fallback";
    }
  }

  document.getElementById('loading-spinner').style.display = 'none';
  document.getElementById('answer-text').textContent = answer;
  document.getElementById('answer-source').textContent = source;
  document.getElementById('answer-area').style.display = 'block';
}

function searchCachedDataset(query) {
  if (!cachedDataset || cachedDataset.length === 0) return null;
  
  const words = query.toLowerCase().split(/\s+/);
  let bestMatch = null;
  let maxScore = 0;

  for (const item of cachedDataset) {
    let score = 0;
    const qWords = item.question.toLowerCase().split(/\s+/);
    
    for (const w of words) {
      if (w.length > 3 && item.question.toLowerCase().includes(w)) {
        score++;
      }
    }
    
    if (item.category && query.toLowerCase().includes(item.category.toLowerCase())) {
      score += 2;
    }

    if (score > maxScore) {
      maxScore = score;
      bestMatch = item;
    }
  }

  return maxScore >= 1 ? bestMatch : null;
}

window.showCategory = function(category) {
  const resultsDiv = document.getElementById('browse-results');
  resultsDiv.innerHTML = '';
  
  if (!cachedDataset || cachedDataset.length === 0) {
    resultsDiv.innerHTML = '<p>No data cached. Please connect and sync.</p>';
    return;
  }
  
  const filtered = cachedDataset.filter(i => i.category.toLowerCase() === category.toLowerCase());
  
  if (filtered.length === 0) {
    resultsDiv.innerHTML = `<p>No guides found for ${category}.</p>`;
    return;
  }
  
  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'qa-card';
    
    const qDiv = document.createElement('div');
    qDiv.className = 'qa-question';
    qDiv.textContent = item.question;
    
    const aDiv = document.createElement('div');
    aDiv.className = 'qa-answer';
    aDiv.textContent = item.answer;
    
    qDiv.onclick = () => {
      aDiv.style.display = aDiv.style.display === 'block' ? 'none' : 'block';
    };
    
    card.appendChild(qDiv);
    card.appendChild(aDiv);
    resultsDiv.appendChild(card);
  });
};

async function syncDataset() {
  showToast("Syncing dataset...", "warning");
  try {
    // Attempt to clear caches and re-fetch
    if ('caches' in window) {
      const cache = await caches.open('resqmar-pwa-v1');
      await cache.add('/data/edge_dataset.json');
    }
    await loadDataset();
    const now = new Date().toLocaleTimeString();
    document.getElementById('last-sync-time').textContent = `Last sync: ${now}`;
    showToast(`[OK] Dataset synced: ${cachedDataset.length} questions`, "success");
  } catch (e) {
    showToast("Sync failed. Check connection.", "error");
  }
}

function showToast(message, type) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.style.display = 'block';
  
  if (type === 'success') toast.style.backgroundColor = 'var(--success-color)';
  else if (type === 'error') toast.style.backgroundColor = 'var(--error-color)';
  else toast.style.backgroundColor = 'var(--warning-color)';
  
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3000);
}

function handleInstallPrompt(e) {
  e.preventDefault();
  deferredPrompt = e;
  const installContainer = document.getElementById('install-container');
  installContainer.style.display = 'block';
  
  document.getElementById('install-btn').addEventListener('click', async () => {
    installContainer.style.display = 'none';
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`[PWA] User install choice: ${outcome}`);
    deferredPrompt = null;
  });
}
