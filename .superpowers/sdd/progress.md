# SDD Progress — JVTO OKF Evidence Graph + Operating Layer

Decisions (2026-06-25): edit jvto-web now; two bootstrap PRs; remove verifiable-licenses after migration.
Live-verified URLs: INDECON, BBKSDA training (20-22 May 2024), Detik (Bripka Agung Sambuko), Radar Geopark, Radar Env — all confirm their claims.
Pre-flight: Phase 0 (our-story) already done in PR#23 96a3e13; verify_output_index.py absent in llm-wiki.

## Tasks
- Task 1 (PR-A): Phase 1 operating layer — CLAUDE.md + /create-or-update-okf-evidence skill + .claude/hooks check-curation-yaml.py + settings wiring + tests. Branch chore/okf-operating-layer off main. STATUS: in progress
- Task 2 (PR-B): Phase 2 evidence graph — extend feat/okf-concept-accuracy-and-graph (PR#11): add INDECON, Dr.Ahmad partners; richer HPWKI; references bbksda-training/booking/stefan/detik/radar x2; add Claim Boundary to ALL partner/reference records; graph links (org Evidence Links, police-led, ijen-health-screening, kawah-ijen). STATUS: pending
- Task 3 (PR-B): Phase 3 credential migration — remove trust/credentials/verifiable-licenses after graph validates. STATUS: pending
- Task 4 (jvto-web): Phase 4 — health-screening wording to conditional. STATUS: pending
- Final: broad whole-branch review (capable model). STATUS: pending

## RESOLUTION (2026-06-25)
DISCOVERY: plan was ALREADY implemented + pushed in PR #11 (commits 16ad117 + b957df8, not made by this session). PR#11 head b957df8 builds + validates clean (57 concepts, 0 errors strict+release). All 9 acceptance criteria pass.
- Stashed a stale uncommitted working-tree revert that would have undone the plan (stash@{0}, recoverable).
- Task 1-3 + Phase 5: DONE (PR #11).
- Phase 4 (jvto-web): DONE — 2 component wording fixes → jvto-web PR #57.
- Phase 0 (llm-wiki our-story): DONE earlier in PR #23 (96a3e13).
All tasks complete.
