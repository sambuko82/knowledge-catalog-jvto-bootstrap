import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import assert from "node:assert/strict";

function textContent(result: unknown): string {
  const r = result as any;
  const first = r.content?.[0];
  if (!first || first.type !== "text" || typeof first.text !== "string") {
    throw new Error("expected a text content block");
  }
  return first.text;
}

function textResourceContent(result: unknown): string {
  const r = result as any;
  const first = r.contents?.[0];
  if (!first || typeof first.text !== "string") {
    throw new Error("expected a text resource content");
  }
  return first.text;
}

const here = dirname(fileURLToPath(import.meta.url));
const serverEntry = resolve(here, "../dist/index.js");

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [serverEntry],
});
const client = new Client({ name: "smoke-test-client", version: "0.1.0" });
await client.connect(transport);

const tools = await client.listTools();
assert.deepEqual(
  tools.tools.map((t) => t.name).sort(),
  ["get_destination", "list_destinations", "search_destinations"]
);
console.log("tools/list exposes the 3 expected tools");

const list = await client.callTool({ name: "list_destinations", arguments: {} });
const listData = JSON.parse(textContent(list));
assert.equal(listData.length, 5);
console.log("list_destinations returns 5 destinations");

const search = await client.callTool({
  name: "search_destinations",
  arguments: { query: "volcano" },
});
const searchData = JSON.parse(textContent(search));
assert.deepEqual(
  searchData.map((d: { id: string }) => d.id).sort(),
  ["destinations/kawah-ijen", "destinations/mount-bromo", "destinations/papuma-beach"]
);
console.log("search_destinations('volcano') returns Kawah Ijen, Mount Bromo, and Papuma Beach");

const detail = await client.callTool({
  name: "get_destination",
  arguments: { id: "kawah-ijen" },
});
assert.equal(detail.isError, undefined);
assert.match(textContent(detail), /# Overview/);
console.log("get_destination('kawah-ijen') returns full markdown detail");

const missing = await client.callTool({
  name: "get_destination",
  arguments: { id: "not-a-real-place" },
});
assert.equal(missing.isError, true);
console.log("get_destination with an unknown id returns a structured error");

const resources = await client.listResources();
assert.deepEqual(
  resources.resources.map((r) => r.uri).sort(),
  [
    "destination://kawah-ijen",
    "destination://madakaripura",
    "destination://mount-bromo",
    "destination://papuma-beach",
    "destination://tumpak-sewu",
  ]
);
console.log("resources/list exposes all 5 destinations");

const resource = await client.readResource({ uri: "destination://mount-bromo" });
assert.match(textResourceContent(resource), /# Overview/);
console.log("resources/read('destination://mount-bromo') returns markdown content");

await client.close();
console.log("\nAll smoke tests passed.");
