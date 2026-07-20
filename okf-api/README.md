# JVTO OKF API

Read-only JSON API exposing JVTO's public OKF bundle content, for consumption
by any application (the website, internal tools, etc.) — not tied to the MCP
protocol. Starts with travel guides; more content types are added to the
`CONTENT_TYPES` registry in `src/bundle.ts` as they're needed.

## Setup

    npm install
    npm run build

## Run

    npm start

## Endpoints

- `GET /healthz` — health check.
- `GET /api/travel-guides` — list all travel guides (id, title, description, tags, status, last_verified).
- `GET /api/travel-guides/:slug` — one guide's full frontmatter + markdown body. Accepts a bare slug (`best-time-to-visit`) or the full catalog id (`travel-guides/best-time-to-visit`).

All responses are JSON. CORS is open (`Access-Control-Allow-Origin: *`) since this only ever serves already-public bundle content.

## Data source

Reads only from the public bundle (`okf/bundles/jvto/catalog.json` and
`okf/bundles/jvto/travel-guides/*.md`) — never from curation sources. It
never writes to any file. The bundle is rebuilt from curated YAML via
`python okf/jvto/scripts/build_bundle.py --curated --indexes` (see the root
`CLAUDE.md`); this API picks up bundle changes on its next read/restart —
no caching to invalidate.

## Deploy

Deployed automatically by GitHub Actions on push to the tracked branch (see
`.github/workflows/jvto-okf.yml`), which rsyncs `okf/bundles/jvto/` and this
directory to the VPS, rebuilds, and reloads the `okf-api` pm2 app.
