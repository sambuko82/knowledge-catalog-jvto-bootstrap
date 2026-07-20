#!/usr/bin/env node
import { createServer, type ServerResponse } from "node:http";
import { listConcepts, getConcept } from "./bundle.js";

const HOST = process.env.HOST ?? "127.0.0.1";
const PORT = Number(process.env.PORT ?? 3300);

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  const json = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "access-control-allow-origin": "*",
  });
  res.end(json);
}

const server = createServer((req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, OPTIONS",
      "access-control-allow-headers": "content-type",
    });
    res.end();
    return;
  }

  if (req.method !== "GET") {
    sendJson(res, 405, { error: "method not allowed" });
    return;
  }

  if (url.pathname === "/healthz") {
    sendJson(res, 200, { ok: true });
    return;
  }

  if (url.pathname === "/api/travel-guides") {
    sendJson(res, 200, listConcepts("travel-guides"));
    return;
  }

  const guideMatch = url.pathname.match(/^\/api\/travel-guides\/([^/]+)$/);
  if (guideMatch) {
    const slug = decodeURIComponent(guideMatch[1]);
    const detail = getConcept("travel-guides", slug);
    if (!detail) {
      sendJson(res, 404, { error: `travel guide not found: ${slug}` });
      return;
    }
    sendJson(res, 200, { ...detail.frontmatter, body: detail.body });
    return;
  }

  sendJson(res, 404, { error: "not found" });
});

server.listen(PORT, HOST, () => {
  console.log(`JVTO OKF API listening on http://${HOST}:${PORT}`);
});

process.on("SIGINT", () => process.exit(0));
process.on("SIGTERM", () => process.exit(0));
