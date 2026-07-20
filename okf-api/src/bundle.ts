import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { load as loadYaml } from "js-yaml";

// okf-api/src/bundle.ts -> okf-api/ -> repo root -> okf/bundles/jvto
const BUNDLE_ROOT = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../okf/bundles/jvto"
);

export interface ConceptSummary {
  id: string;
  title: string;
  description: string;
  tags: string[];
  status: string;
  last_verified: string;
}

interface CatalogEntry extends ConceptSummary {
  type: string;
  path: string;
}

interface Catalog {
  concepts: CatalogEntry[];
}

export interface ConceptDetail {
  frontmatter: Record<string, unknown>;
  body: string;
}

function loadCatalog(): Catalog {
  const raw = readFileSync(join(BUNDLE_ROOT, "catalog.json"), "utf-8");
  return JSON.parse(raw) as Catalog;
}

function toSummary(entry: CatalogEntry): ConceptSummary {
  return {
    id: entry.id,
    title: entry.title,
    description: entry.description,
    tags: entry.tags,
    status: entry.status,
    last_verified: entry.last_verified,
  };
}

// Content type registry. Each entry maps an OKF `type` value (as it appears
// in catalog.json) to the id prefix its concepts use, so bare slugs (e.g.
// "best-time-to-visit") can be normalized to full catalog ids (e.g.
// "travel-guides/best-time-to-visit"). Add more entries here as the API
// grows beyond travel guides.
const CONTENT_TYPES = {
  "travel-guides": { okfType: "Travel Guide", idPrefix: "travel-guides/" },
} as const;

export type ContentTypeKey = keyof typeof CONTENT_TYPES;

function entriesFor(key: ContentTypeKey): CatalogEntry[] {
  const { okfType } = CONTENT_TYPES[key];
  return loadCatalog().concepts.filter((entry) => entry.type === okfType);
}

export function listConcepts(key: ContentTypeKey): ConceptSummary[] {
  return entriesFor(key).map(toSummary);
}

// Destination markdown files start with a `---`-delimited YAML frontmatter
// block; everything after the closing `---` is the body (already-formatted
// markdown).
const FRONTMATTER_PATTERN = /^---\n([\s\S]*?)\n---\n?/;

function parseFrontmatter(content: string): ConceptDetail {
  const match = content.match(FRONTMATTER_PATTERN);
  if (!match) {
    throw new Error("markdown file is missing a frontmatter block");
  }
  const frontmatter = loadYaml(match[1]) as Record<string, unknown>;
  const body = content.slice(match[0].length);
  return { frontmatter, body };
}

export function getConcept(key: ContentTypeKey, id: string): ConceptDetail | undefined {
  const { idPrefix } = CONTENT_TYPES[key];
  const normalized = id.includes("/") ? id : `${idPrefix}${id}`;
  const entry = entriesFor(key).find((e) => e.id === normalized);
  if (!entry) return undefined;
  const raw = readFileSync(join(BUNDLE_ROOT, entry.path), "utf-8");
  return parseFrontmatter(raw);
}
