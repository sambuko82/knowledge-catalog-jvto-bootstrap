import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { load as loadYaml } from "js-yaml";

// mcp-server/src/bundle.ts -> mcp-server/ -> repo root -> okf/bundles/jvto
const BUNDLE_ROOT = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../okf/bundles/jvto"
);

export interface DestinationSummary {
  id: string;
  title: string;
  description: string;
  tags: string[];
  status: string;
  last_verified: string;
}

interface CatalogEntry extends DestinationSummary {
  type: string;
  path: string;
}

interface Catalog {
  concepts: CatalogEntry[];
}

export interface DestinationDetail {
  frontmatter: Record<string, unknown>;
  body: string;
}

function loadCatalog(): Catalog {
  const raw = readFileSync(join(BUNDLE_ROOT, "catalog.json"), "utf-8");
  return JSON.parse(raw) as Catalog;
}

function toSummary(entry: CatalogEntry): DestinationSummary {
  return {
    id: entry.id,
    title: entry.title,
    description: entry.description,
    tags: entry.tags,
    status: entry.status,
    last_verified: entry.last_verified,
  };
}

function destinationEntries(): CatalogEntry[] {
  return loadCatalog().concepts.filter((entry) => entry.type === "Destination");
}

export function listDestinations(): DestinationSummary[] {
  return destinationEntries().map(toSummary);
}

export function searchDestinations(query: string): DestinationSummary[] {
  const needle = query.toLowerCase();
  return listDestinations().filter(
    (entry) =>
      entry.title.toLowerCase().includes(needle) ||
      entry.description.toLowerCase().includes(needle) ||
      entry.tags.some((tag) => tag.toLowerCase().includes(needle))
  );
}

function findCatalogEntry(id: string): CatalogEntry | undefined {
  const normalized = id.includes("/") ? id : `destinations/${id}`;
  return destinationEntries().find((entry) => entry.id === normalized);
}

// Destination markdown files start with a `---`-delimited YAML frontmatter
// block; everything after the closing `---` is the body (already-formatted
// markdown, including a "# Citations" heading where citations exist).
const FRONTMATTER_PATTERN = /^---\n([\s\S]*?)\n---\n?/;

function parseFrontmatter(content: string): DestinationDetail {
  const match = content.match(FRONTMATTER_PATTERN);
  if (!match) {
    throw new Error("markdown file is missing a frontmatter block");
  }
  const frontmatter = loadYaml(match[1]) as Record<string, unknown>;
  const body = content.slice(match[0].length);
  return { frontmatter, body };
}

export function getDestination(id: string): DestinationDetail | undefined {
  const entry = findCatalogEntry(id);
  if (!entry) return undefined;
  const raw = readFileSync(join(BUNDLE_ROOT, entry.path), "utf-8");
  return parseFrontmatter(raw);
}

export function listDestinationResourceUris(): {
  uri: string;
  slug: string;
  title: string;
}[] {
  return destinationEntries().map((entry) => {
    const slug = entry.id.replace("destinations/", "");
    return { uri: `destination://${slug}`, slug, title: entry.title };
  });
}
