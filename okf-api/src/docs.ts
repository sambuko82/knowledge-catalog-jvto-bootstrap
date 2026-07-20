const BASE_URL = "https://okf.javavolcano-touroperator.com";

interface EndpointDoc {
  method: string;
  path: string;
  summary: string;
  example: { request: string; response: string };
}

const ENDPOINTS: EndpointDoc[] = [
  {
    method: "GET",
    path: "/healthz",
    summary: "Health check.",
    example: {
      request: `curl ${BASE_URL}/healthz`,
      response: `{ "ok": true }`,
    },
  },
  {
    method: "GET",
    path: "/api/travel-guides",
    summary: "List every travel guide (id, title, description, tags, status, last_verified).",
    example: {
      request: `curl ${BASE_URL}/api/travel-guides`,
      response: `[
  {
    "id": "travel-guides/best-time-to-visit",
    "title": "Best Time to Visit East Java",
    "description": "When to go — the dry season gives the clearest ...",
    "tags": ["travel-guide", "planning", "season", "weather"],
    "status": "reviewed",
    "last_verified": "2026-06-23"
  },
  ...
]`,
    },
  },
  {
    method: "GET",
    path: "/api/travel-guides/:slug",
    summary:
      "One guide's full frontmatter plus markdown body. Accepts a bare slug (best-time-to-visit) or the full catalog id (travel-guides/best-time-to-visit).",
    example: {
      request: `curl ${BASE_URL}/api/travel-guides/best-time-to-visit`,
      response: `{
  "type": "Travel Guide",
  "title": "Best Time to Visit East Java",
  "status": "reviewed",
  "last_verified": "2026-06-23",
  ...
  "body": "# Overview\\n\\nThere is no universally bad time to visit ..."
}`,
    },
  },
];

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderEndpoint(ep: EndpointDoc): string {
  return `
    <section class="endpoint">
      <div class="ep-head">
        <span class="method">${ep.method}</span>
        <code class="path">${escapeHtml(ep.path)}</code>
      </div>
      <p class="summary">${escapeHtml(ep.summary)}</p>
      <div class="example">
        <div class="example-label">Request</div>
        <pre><code>${escapeHtml(ep.example.request)}</code></pre>
        <div class="example-label">Response</div>
        <pre><code>${escapeHtml(ep.example.response)}</code></pre>
      </div>
    </section>`;
}

export function renderDocsHtml(): string {
  const rows = ENDPOINTS.map(renderEndpoint).join("\n");
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>JVTO OKF API — Documentation</title>
<style>
:root {
  --bg: #F7F8F3;
  --surface: #FFFFFF;
  --text: #1B1E1C;
  --text-muted: #5B6058;
  --border: #DDE0D6;
  --accent: #0E7C86;
  --accent-soft: #DCEFEE;
  --mono: ui-monospace, 'SF Mono', 'IBM Plex Mono', Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14181A;
    --surface: #1B2023;
    --text: #E9EBE6;
    --text-muted: #A2A89E;
    --border: #2B3134;
    --accent: #4FD9E8;
    --accent-soft: #1B3A3D;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
}
.wrap { max-width: 760px; margin: 0 auto; padding: 56px 24px 96px; }
header { margin-bottom: 40px; }
.eyebrow {
  font-size: 12.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 10px;
}
h1 { font-size: 1.9rem; margin: 0 0 12px; letter-spacing: -0.01em; }
.lede { color: var(--text-muted); max-width: 60ch; margin: 0 0 18px; }
.base-url {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 13.5px;
  background: var(--accent-soft); color: var(--accent);
  padding: 6px 12px; border-radius: 8px;
}
.notes { font-size: 13.5px; color: var(--text-muted); margin-top: 16px; }
.notes li { margin-bottom: 4px; }
h2.section-title {
  font-size: 12.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--text-muted); margin: 40px 0 16px; padding-top: 24px; border-top: 1px solid var(--border);
}
.endpoint {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 20px 22px; margin-bottom: 16px;
}
.ep-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.method {
  font-family: var(--mono); font-size: 12px; font-weight: 700;
  background: var(--accent); color: var(--surface); padding: 2px 8px; border-radius: 5px;
}
.path { font-family: var(--mono); font-size: 14.5px; }
.summary { color: var(--text-muted); font-size: 14.5px; margin: 0 0 14px; }
.example-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--text-muted); margin: 12px 0 6px;
}
.example-label:first-child { margin-top: 0; }
pre {
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 12px 14px; overflow-x: auto; margin: 0; font-family: var(--mono);
  font-size: 12.5px; line-height: 1.6;
}
footer { margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 13px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">API Reference</div>
    <h1>JVTO OKF API</h1>
    <p class="lede">Read-only JSON API exposing JVTO's public OKF bundle content. No authentication required, CORS is open, and every response is JSON.</p>
    <div class="base-url">${BASE_URL}</div>
    <ul class="notes">
      <li>All content comes from <code>okf/bundles/jvto/</code> — already-curated, public-safe knowledge, never raw operational data.</li>
      <li>Currently serves travel guides only; more content types (destinations, policies, etc.) are added as they're needed.</li>
    </ul>
  </header>

  <h2 class="section-title">Endpoints</h2>
  ${rows}

  <footer>
    knowledge-catalog-jvto-bootstrap — deployed automatically on push via GitHub Actions.
  </footer>
</div>
</body>
</html>`;
}
