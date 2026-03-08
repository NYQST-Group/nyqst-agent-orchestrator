# [NX-012] Add optional NDJSON fetch streaming for run events (Superagent-style) alongside SSE

**Why**
Some environments/proxies handle chunked fetch streaming more reliably than native EventSource, and Superagent uses NDJSON over `fetch + ReadableStream`.

**Goal**
- Keep SSE endpoint (current) but add an alternative:
  - `GET /api/v1/streams/runs/{run_id}?transport=ndjson`
  - or `GET /api/v1/runs/{run_id}/stream.ndjson`

**Implementation**
- Backend: same event payloads; different framing:
  - SSE: `data: {json}\n\n`
  - NDJSON: `{json}\n`
- Frontend: add a hook that can use either transport.

**Acceptance criteria**
- Both transports deliver identical event objects.
- A feature flag can switch transport.

