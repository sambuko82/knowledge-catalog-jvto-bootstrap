#!/usr/bin/env node
import { createServer } from "node:http";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createDestinationsMcpServer } from "./server.js";

const HOST = process.env.HOST ?? "127.0.0.1";
const PORT = Number(process.env.PORT ?? 3300);

function jsonRpcError(code: number, message: string) {
  return JSON.stringify({ jsonrpc: "2.0", error: { code: -32000, message }, id: null });
}

const httpServer = createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

  if (url.pathname === "/healthz") {
    res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify({ ok: true }));
    return;
  }

  if (url.pathname !== "/mcp") {
    res.writeHead(404, { "content-type": "application/json" }).end(jsonRpcError(-32000, "Not found."));
    return;
  }

  if (req.method !== "POST") {
    res.writeHead(405, { "content-type": "application/json" }).end(jsonRpcError(-32000, "Method not allowed."));
    return;
  }

  // Stateless: a fresh server + transport per request, no session state kept between calls.
  const server = createDestinationsMcpServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

  try {
    await server.connect(transport);
    await transport.handleRequest(req, res);
  } catch (error) {
    console.error("Error handling MCP request:", error);
    if (!res.headersSent) {
      res.writeHead(500, { "content-type": "application/json" }).end(jsonRpcError(-32603, "Internal server error."));
    }
  } finally {
    res.on("close", () => {
      transport.close();
      server.close();
    });
  }
});

httpServer.listen(PORT, HOST, () => {
  console.log(`JVTO destinations MCP server (Streamable HTTP) listening on http://${HOST}:${PORT}/mcp`);
});

process.on("SIGINT", () => process.exit(0));
process.on("SIGTERM", () => process.exit(0));
