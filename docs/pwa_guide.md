# ResQ-MAR Progressive Web App (PWA) Guide

## 1. What is the ResQ-MAR PWA?
The ResQ-MAR Progressive Web App (PWA) is a specialized, mobile-first interface designed for field responders. Unlike the main dispatcher dashboard, the PWA is built to survive in austere environments where internet connectivity is compromised. 
It works completely offline after the first load and provides AI emergency guidance via a local edge model (Phi-3-mini) or a securely cached disaster response dataset.

## 2. Installation
To install the PWA on your device:
- Step 1: Start the EdgeAgent by running `ollama run phi3:mini` on port 11435.
- Step 2: Start the FastAPI backend with `python -m uvicorn src.api.main:app --reload`
- Step 3: Open your mobile or desktop browser to `http://localhost:8000/frontend/pwa/index.html`
- Step 4: Click the "Install App" button or select "Add to Home Screen" from your browser menu.
- Step 5: The app will install as a standalone, native-like application on your home screen or desktop.

## 3. How It Works
- Online mode: When connected to the local network, the PWA queries the Phi-3-mini model via the EdgeAgent API (`/edge/query`) for live, generative AI responses.
- Offline mode: If the connection drops or the EdgeAgent is down, the app intercepts the network failure and searches a locally cached 50-question disaster dataset for the best keyword match.
- Background sync: (Where supported) the app queues questions and sends them when the connection is restored.
- Cache First strategy: The Service Worker caches the app shell (HTML, JS, CSS), ensuring the app loads instantly even with airplane mode enabled.

## 4. Features
- Ask emergency questions using natural language.
- Browse by disaster category (flood, fire, earthquake, medical, general).
- Emergency numbers are hardcoded and always available offline.
- Real-time connection status indicator (Online, Edge Mode, Offline).
- Dataset sync button to manually pull the latest procedures.

## 5. Architecture
- Service Worker (`sw.js`): Intercepts all network requests. Caches the app shell and dataset during the `install` phase.
- IndexedDB/Cache API: Stores the Q&A dataset natively on the device.
- Fetch API: Connects to the FastAPI backend, timing out gracefully if the server is unreachable.
- Keyword matching algorithm: A lightweight JavaScript function that finds the best cached answer by calculating word overlap.

## 6. Browser Support
- Chrome/Edge: Full support (service worker, background sync, install prompt).
- Firefox: Full support for offline capabilities.
- Safari iOS: Partial support (no background sync, must be installed manually via Share -> Add to Home Screen).
- Offline capability works robustly across all modern browsers.

## 7. Troubleshooting
- "Install button not showing": Use Google Chrome or Microsoft Edge. Ensure you are accessing via `localhost` or a secure `https` context.
- "Edge model not responding": Verify Ollama is running the `phi3:mini` model and the EdgeAgent script is active on port 11435.
- "No cached answers": Click "Sync Now" while online to pull the dataset.
- "App not updating": Unregister the service worker in DevTools -> Application -> Service Workers, then refresh.

## 8. Future Enhancements
- Voice input integration via the Web Speech API for hands-free operation.
- Push notifications for broadcasted emergency alerts.
- Geolocation tracking for nearest shelter routing.
- Multi-language support (Sinhala, Tamil) for broader accessibility.
