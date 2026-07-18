import { test } from "node:test";
import assert from "node:assert/strict";
import { listDestinations, searchDestinations, getDestination } from "./bundle.js";

test("listDestinations returns all five public destinations", () => {
  const destinations = listDestinations();
  assert.equal(destinations.length, 5);
  const ids = destinations.map((d) => d.id).sort();
  assert.deepEqual(ids, [
    "destinations/kawah-ijen",
    "destinations/madakaripura",
    "destinations/mount-bromo",
    "destinations/papuma-beach",
    "destinations/tumpak-sewu",
  ]);
});

test("searchDestinations matches on tag/description substring", () => {
  // kawah-ijen and mount-bromo: "volcano" in tags and description.
  // papuma-beach: "volcano" appears in its description too ("JVTO's volcano circuits").
  const results = searchDestinations("volcano");
  const ids = results.map((d) => d.id).sort();
  assert.deepEqual(ids, [
    "destinations/kawah-ijen",
    "destinations/mount-bromo",
    "destinations/papuma-beach",
  ]);
});

test("searchDestinations is case-insensitive and matches description text", () => {
  const results = searchDestinations("NIAGARA");
  assert.equal(results.length, 1);
  assert.equal(results[0].id, "destinations/tumpak-sewu");
});

test("getDestination accepts a bare slug", () => {
  const detail = getDestination("kawah-ijen");
  assert.ok(detail);
  assert.equal(detail.frontmatter.title, "Kawah Ijen");
  assert.match(detail.body, /# Overview/);
});

test("getDestination accepts the full catalog id and matches the bare-slug result", () => {
  const bySlug = getDestination("kawah-ijen");
  const byId = getDestination("destinations/kawah-ijen");
  assert.deepEqual(byId, bySlug);
});

test("getDestination returns undefined for an unknown id", () => {
  assert.equal(getDestination("not-a-real-place"), undefined);
});
