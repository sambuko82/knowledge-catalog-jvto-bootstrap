---
name: create-or-update-okf-evidence
description: Create or update a public JVTO OKF evidence concept (Partner, Reference, Trust Claim, Credential, Destination, Policy) through the single curation pipeline, with live claim verification and strict/release validation. Use when adding or changing any concept in this repo's public bundle.
---

# /create-or-update-okf-evidence

One pipeline only. This skill does not introduce a separate publication process —
it drives the existing curation flow and reuses the verified-curation discipline in
`okf/jvto/skills/jvto-okf-verified-curation/SKILL.md` (read that first for the
claim-by-claim evidence rules and the verification-report format).

## Boundaries (from CLAUDE.md)

- Public concepts are created ONLY by editing `okf/jvto/curation/approved/*.yaml`
  and running `build_bundle.py --curated --indexes`. Never hand-edit
  `okf/bundles/jvto/**` and never create an `okf/` concept store in another repo.
- Status reflects evidence actually checked: `reviewed` (first-party / homepage),
  `qualified` (publishable with a visible limitation), `verified` (a live, publicly
  readable authority/first-party source supports the exact wording). Never set
  `verified` because llm-wiki says so.
- Every Partner or Reference concept must contain a `# Claim Boundary` section.
- Keep login-gated registry routes (KKI, SatuSehat) in the internal verification
  report only — never as public citations. PII / rates / secrets never go public.

## Sequence

1. **Read the source matrix.** For the concept(s) being added/changed, list each
   material claim and its evidence URL(s).
2. **Check each material claim against each URL** (live). Use a stealth-capable
   fetch (Firecrawl) for bot-protected sites; record the observed value + date.
   A page that 404s / is login-gated / does not name JVTO downgrades or blocks the
   claim — it does not get `verified`.
3. **Write or update the curation YAML only** (`okf/jvto/curation/approved/*.yaml`).
   Set status from step 2. Include `# Claim Boundary` for Partner/Reference. Use
   bundle-relative `.md` links and full HTTPS citation URLs. If a record is removed,
   `rm` its stale built `.md` under `okf/bundles/jvto/`.
4. **Generate bundle Markdown:** `python okf/jvto/scripts/build_bundle.py --curated --indexes`.
5. **Generate a verification report** (internal, not in the public bundle) at
   `okf/jvto/build/verification/<concept-id>-verification.md`: per-claim status,
   the URL checked, observed value/date, and any gated/PII routes kept internal.
6. **Run strict validation:** `python okf/jvto/scripts/validate_okf.py --strict-links`.
7. **Run release validation:** `python okf/jvto/scripts/validate_okf.py --release --strict-links`.
8. **Review the generated diff** under `okf/bundles/jvto/` — confirm only intended
   files changed and every internal link resolves.
9. **Report** included claims, qualified claims (with the limitation), and excluded
   claims (with the reason). Surface any concept that could not reach its intended
   status and why.

## Removal / migration

When replacing a broad concept with granular ones, build and validate the
replacement graph first, clear every inbound link to the broad concept, then remove
its record AND its built `.md`, and re-run strict + release validation.
