# METRICS.md

## Performance
| Metric | Methodology | Raw Evidence | Final Value |
|---|---|---|---|

### PERFORMANCE
| Metric | Methodology | Raw Evidence | Final Value |
|---|---|---|---|
| OSRM routing latency | Attempted API / Subprocess | Connection Error / Service Down | UNMEASURABLE: Docker OSRM container offline (HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /route/v1/driving/77.2090,28.6139;75.7873,26.9124?overview=false (Caused by ConnectTimeoutError(<HTTPConnection(host='localhost', port=5000) at 0x1bac9844230>, 'Connection to localhost timed out. (connect timeout=2)'))) |
| OSRM route optimality | Attempted API / Subprocess | Connection Error / Service Down | UNMEASURABLE: Docker OSRM container offline |
| Whisper voice processing | Attempted API / Subprocess | Connection Error / Service Down | UNMEASURABLE: Whisper module error |
| Translation latency | Time LanguageService.translate(mocked) | Translated in 0.00ms | 0.00 ms |
| Live tracking frame rate | Inspect frontend/components/live_tracker.py time.sleep loop | time.sleep(0.5) | 2 FPS (0.5s interval) |

### ACCURACY
| Metric | Methodology | Raw Evidence | Final Value |
|---|---|---|---|
| Severity precision & recall | Parse evaluation/results/benchmark_report.json | Precision: 1.0, Recall: 1.0 | P:100.0%, R:100.0%, F1:100.0% |
| State/language detection accuracy | Loop over 10 metros in METROS | Chennai->Tamil Nadu, Mumbai->Maharashtra, Kolkata->West Bengal, Bangalore->Karnataka, Delhi->Delhi, Hyderabad->Telangana, Ahmedabad->Gujarat, Pune->Maharashtra, Jaipur->Rajasthan, Lucknow->Uttar Pradesh | 10/10 (100%) |
| Hazard intersection accuracy | shapely point-in-polygon check for Chennai vs Delhi | Chennai: ['cyclone'], Delhi: ['seismic'] | 2/2 Verified |
| RAG relevance | Query ChromaDB | cannot import name 'ChromaDBClient' from 'src.rag.embeddings' (D:\Projects & Internships\resq-mar\src\rag\embeddings.py) | Fallback to file scan |

### RESILIENCE
| Metric | Methodology | Raw Evidence | Final Value |
|---|---|---|---|
| Offline resilience | Architectural component audit (Ollama, OSRM, Whisper) | Core routing + text generation require 0 cloud endpoints | 100% Offline Capable |
| Cost per 10,000 runs | Calculate API footprint | Local models used for intake, planner, router | $0.00 (Excluding Electricity) |
| API fallback behavior | Instantiate agents with None keys | LiveAwareness falls back to empty context, Vision falls back to disabled | 0 Crashes, Graceful degradation |

### COVERAGE
| Metric | Methodology | Raw Evidence | Final Value |
|---|---|---|---|
| Language coverage | Extract from geo_lookup.py dict | Tamil, Telugu, Hindi, Bengali, Marathi, Kannada, Gujarati | 7 Regional + English |
