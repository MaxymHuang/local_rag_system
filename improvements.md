# Improvement Road-Map

This document collects high-impact ideas to make the File Finder RAG system faster, more reliable, and more pleasant to use.

---
## Efficiency & Robustness

1. **Persist & Incrementally Update the Vector Index**
   - Serialize the FAISS index with `faiss.write_index`.
   - Store a checksum (mtime + size or SHA-1) per file.
   - On start-up, only (re-)embed files whose checksum changed.
   - → Cold-start moves from minutes → seconds for large corpora.

2. **Switch to an Approximate ANN Index**
   - `IndexFlatL2` is exact and O(N).
   - Replace with IVF-PQ or HNSW (`faiss.IndexIVFFlat`, `faiss.IndexHNSWFlat`).
   - Parameterise the index type so power users can pick accuracy vs. latency.

3. **Parallel / GPU Embedding Pipeline**
   - `SentenceTransformer.encode` supports `device="cuda"`, `batch_size`, `use_amp=True`.
   - For CPU-only boxes, embed batches with `ProcessPoolExecutor`.

4. **Move Long-Running Work Off the Flask Thread**
   - Push index building & LLM summarisation to a task queue (Celery, RQ, or ThreadPool).
   - Return a task-id; UI polls or uses Web-Sockets/SSE.

5. **Streaming / Chunked Summarisation**
   - Chunk large files, summarise each chunk, then merge (Map-Reduce).
   - Stream partial summaries back to the browser for instant feedback.

6. **Harden File Access & Path Handling**
   - Reject path traversal (`..`) and whitelist the root directory.
   - Sandbox summarisation in a worker process.
   - Add rate-limiting and request size limits to every endpoint.

7. **Observability & Auto-Recovery**
   - Structured logging (loguru / structlog) & exception tracking (Sentry).
   - Docker `HEALTHCHECK` that pings `/status`; `restart: always` in compose.
   - Prometheus metrics for query latency, index size, Ollama round-trip times.

---
## User Experience

1. **Real-Time Progress Indicators**
   - Determinate progress bar during indexing (`files_processed / total`).
   - Stream tokens while summarising (EventSource / WebSocket).

2. **Rich Search Result Cards**
   - File-type icons, size, last-modified date, and a snippet preview.
   - "Open", "Download", and "Copy path" quick actions.

3. **Faceted & Advanced Filters**
   - Filter by file type, date range, or directory path.
   - "Sort by" relevance / last modified / path.

4. **Conversation-Aware Retrieval**
   - Every chat message runs retrieval; feed chunks into the LLM to answer.
   - Keeps chat grounded in the user's own files.

5. **Session Persistence & Collaboration**
   - Store past searches & summaries per user (SQLite / Redis).
   - Export (Markdown/PDF) or share-link functionality.

6. **On-Boarding & Error Clarity**
   - First-run wizard checks Ollama, GPU, and walks through model download.
   - Standard JSON error schema (`code`, `message`, `details`).

7. **Accessibility & Theming**
   - Dark/light/system themes (`prefers-color-scheme`).
   - Keyboard navigation & ARIA labels for all UI elements.

---
## Low-Effort / High-Value Quick Wins

- Cache Ollama responses for identical summarisation requests (LRU).
- Add `pytest --cov` in CI; gate merges on >90 % coverage.
- Switch to FastAPI for async handling—automatic OpenAPI docs.
- Ship a "demo" dataset and `make demo` target for first-time users. 