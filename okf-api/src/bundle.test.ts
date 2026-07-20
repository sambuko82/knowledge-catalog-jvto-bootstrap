import { test } from "node:test";
import assert from "node:assert/strict";
import { listConcepts, getConcept } from "./bundle.js";

test("listConcepts('travel-guides') returns all seven guides", () => {
  const guides = listConcepts("travel-guides");
  assert.equal(guides.length, 7);
  const ids = guides.map((g) => g.id).sort();
  assert.deepEqual(ids, [
    "travel-guides/best-time-to-visit",
    "travel-guides/bromo-vs-ijen",
    "travel-guides/how-many-days",
    "travel-guides/packing-and-fitness",
    "travel-guides/safety-on-tours",
    "travel-guides/surabaya-vs-bali-starting-point",
    "travel-guides/weather-and-closures",
  ]);
});

test("getConcept accepts a bare slug", () => {
  const detail = getConcept("travel-guides", "best-time-to-visit");
  assert.ok(detail);
  assert.equal(detail.frontmatter.title, "Best Time to Visit East Java");
  assert.match(detail.body, /# Overview/);
});

test("getConcept accepts the full catalog id and matches the bare-slug result", () => {
  const bySlug = getConcept("travel-guides", "best-time-to-visit");
  const byId = getConcept("travel-guides", "travel-guides/best-time-to-visit");
  assert.deepEqual(byId, bySlug);
});

test("getConcept returns undefined for an unknown slug", () => {
  assert.equal(getConcept("travel-guides", "not-a-real-guide"), undefined);
});
