# Re-Baseline Note — read this first

**Date:** 2026-06-25.

## What happened
The session opened with a git snapshot reporting `HEAD = a25fbd1 (#2)` and a bundle of **one** concept
(`organization.md`). The first exploration pass was performed against that picture. It was **stale**:
the real `main` had already advanced to **`6e1a73c (#8)`** with **46 published concepts** across
destinations (5), policies (9), reviews (3), tours (16), travel-guides (7), trust/claims (4),
trust/credentials (2). The local ref caught up partway through the session, exposing the gap.

Everything in this `workspace/` directory has been **re-done against the real `6e1a73c` bundle.** The
earlier "near-empty bundle / publish ~18 concepts from scratch" framing is retracted — most of those
concepts already exist and are well-built.

## What changed in the conclusions
1. **The bundle is already substantial and largely correct.** Review counts are current, not stale:
   `reviews/google-maps.md` cites **4.9 / ~123** (2026-05-26), `trustpilot` **4.8 / 51** (2026-05-18),
   `tripadvisor` **4.95 / ~21**. The stale `92` / `47` live only in the *raw SSOT JSON* and on the
   *live homepage* — **not** in the bundle.
2. **#8 already implemented the Partner/Reference citation rule** (my earlier "taxonomy gap" was
   already closed). The original PR built on the stale base would have *reverted* it; that PR (#9) was
   **closed**.
3. **Adversarial verification refuted three "authority" claims I had initially trusted.** A clean,
   independent fetch of the Satusehat practitioner URL returns *"Laman profil publik belum tersedia"*
   (public profile not yet available — login-gated); the doctor's name/SIP/expiry are **not** publicly
   readable, and publishing them would be a PII/credential exposure. The AHU legal-entity decree
   string is **not** on the public site (the only public AHU number is the HPWKI association decree, a
   different credential). These are now **deferred / do_not_publish**, matching what the bundle already
   does (it never cited them).
4. **The genuinely-empty families are only `trust/partners/` and `references/`.** Tours (16) match the
   homepage's "16 tours"; the package-count "conflict" is resolved in the bundle.

## Net real findings (the corrected audit)
- **Concrete factual fix:** `destinations/kawah-ijen.md` calls **2,386 m the "summit"**; that is the
  crater-rim elevation — the Ijen complex summit is ~2,769–2,799 m (Wikipedia / Smithsonian GVP).
- **Strengthen-able:** `mount-bromo` and `madakaripura` can move to `verified` with authority
  citations (Smithsonian GVP; Probolinggo Regency tourism office, which states Madakaripura *is* the
  tallest in Java). `tumpak-sewu` "multi-tier" → "curtain/semicircular".
- **Net-new:** `references/` and `trust/partners/` families (HPWKI is cleanly net-new; BBKSDA must be
  framed as the *governing authority*, not a commercial partner; ISIC as a directory listing).
- **Live-website (not bundle) bug:** homepage still shows Google **92** vs the canonical **123** →
  owner action on the site, plus a defensive validator guard (JVTO-11) so it can never enter the bundle.

## Process lesson (recorded for future audits)
Trust the working tree over the session snapshot: re-run `git log`/`ls-files` before drawing
"what exists" conclusions, and **adversarially verify any authority claim with an independent fetch**
before classifying it `verified` — the first single-pass WebFetch of the Satusehat URL returned a
fabricated "valid record" that the adversarial pass corrected.
