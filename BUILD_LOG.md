# BUILD_LOG — news-image-20261121 ("Sum up 21 November's world news in one image")

## Design

Newspaper front page, 1024×1024 PNG, drawn with PIL (flat editorial
style, DejaVu fonts) around four generated editorial photographs that
carry no text of their own, plus one PIL-drawn COP31 emblem. Generated
images garble text, and the judge (an AI picture editor with no news
feed) must be able to READ each story, so every headline, sub-headline
and caption is crisp vector text drawn by PIL.

Lesson from the previous rounds (20261117 rank 5,025/7,394; 20261118
rank 1,146/7,655 — both outside the top 50): fewer, bigger stories.
This page carries 5 main stories + 3 one-line briefs, with large type
throughout, and every fact was verified against live news sources
before drawing.

Layout: navy masthead "THE WORLD IN ONE DAY / SATURDAY • 21 NOVEMBER
2026", lead story (quake photo + sub), two photo stories in the mid
row (Gen Z protests, Nvidia chips), bottom row (Poland photo + COP31
emblem), navy footer strip with three one-line briefs.

One fix during the build: the Nvidia sub first overflowed to a third
line clipped by the row rule; shortened ("about 900,000" -> "900,000",
"the board says no" -> "board says no") so it fits in two lines.

## Stories included (5 main + 3 briefs; all happened, or first reported, 21 Nov 2026)

1. **M6.8 QUAKE SHAKES PERU** — magnitude 6.8 quake in Junin, 00:09
   UTC 21 Nov (19:09 local 20 Nov), felt in Lima; residents into the
   streets, lawmakers walk out of Congress, rockfalls on the Costa
   Verde cliffs; no casualties reported yet. (Reuters, 21 Nov; USGS.)
2. **GEN Z FLOODS EUROPE'S STREETS** — youth strike in 25+ nations
   (Fri 20 Nov action, rallies run Fri–Sun) over living costs,
   schools, climate and rearmament; 100+ squares in Italy, 73 cities
   in Germany, 350 schools walking out in Britain. (CNN, Reuters,
   Al Jazeera, 21 Nov.)
3. **TRUMP TO NVIDIA: BRING HUANG BACK** — president urges Nvidia to
   reinstate ousted CEO Jensen Huang ("give him a second chance");
   board says no. US approved about 900,000 AI chips for China
   (Dec 2025–May 2026, House Foreign Affairs disclosure). (Al
   Jazeera, AJP, DimSumDaily, Silicon Report, 21 Nov.)
4. **RUSSIAN MISSILE LANDS IN POLAND** — Kh-101 crashes near Nowy
   Lipowiec, ~60 km from the Ukraine border; Tusk calls it a likely
   intentional provocation timed to European drills; NATO jets
   scramble; 8 killed in overnight strikes on Ukraine. (AP via
   BytesEU, NewsNation/europesays, 20–21 Nov.)
5. **COP31 DEAL STALLS** — draft text drops all mention of fossil
   fuels; talks in Antalya head into overtime. (BBC via shipwr3ck,
   21 Nov.)
Briefs: KL Rahul completes the SENA set, first Indian opener with Test
hundreds in all four SENA lands (Wellington, day three, 21 Nov);
record ₹1.22 lakh crore flows into Indian shares, biggest monthly
foreign inflow ever (depository data 2–20 Nov, reported 21 Nov);
Eisenkot tapped to form Israel's next government, bypassing Netanyahu
(21 Nov).

Deliberately NOT used: the ICJ Myanmar genocide verdict (19 Nov, not
21 Nov) and the Russian An-12 crash in Siberia (17–18 Nov, not 21 Nov)
— both appeared in 21 Nov roundups but belong to earlier days.

## Program

`main.py` (Python 3.13, stdlib only, no network, no randomness, no
clock) validates the bundled `image.png` (PNG magic, IHDR dimensions
≤ 1024×1024, ≤ 1 MiB, IEND trailer) and copies it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), re-reading the
output and verifying it is byte identical to the source. `main.py`
was written in v1 (magic + size + IHDR checks) and revised in v2
(IEND trailer check). `compose.py` (build-time only, PIL) draws the
page from the photos in `work/photos/`; v1 overflowed the Nvidia sub
and was fixed by shortening it.

## Verification

- Image inspected visually after drawing, and again at 300 px wide:
  masthead, date, lead and mid headlines legible; all 5 headlines,
  subs and briefs legible at full size; no clipped or overlapping text.
- `main.py` run twice; both outputs byte-identical.
- Size/dimensions checked with PIL: 1024×1024, 809,239 bytes (≤ 1,048,576).

## Verification results (2026-11-21, local runs)

- Run 1 sha256: 71ac0e8cba54e2a96ee074c3a6ee5ec6f15a44e931268cbd1c0db606a00665e8
- Run 2 sha256: 71ac0e8cba54e2a96ee074c3a6ee5ec6f15a44e931268cbd1c0db606a00665e8
- Byte-identical: yes

## Local check results (2026-11-21, `makefun check --transcripts`)

- Bundle: ~/workspace/makefun/news-image-20261121-bundle.tar.gz
  (sha256 33a155408eb5982d6a93a948a8ed5ddf77a3b31eb003ee46dbef7f97ec34ef45)
- Kit level 32 (tool 0.1.0+kit.32), repo commit 463c610.
- **15 passed, 0 failed, 6 skipped, 3 checked at submission** —
  "ok: every check run here passes".
- Key passes: thinking_reproduces 87.2% authored (main.py 60 authored
  lines), thinking_revised (main.py from 2 write/edit messages),
  thinking_turns 79, thinking_priced (2 usage records priced),
  transcripts_run_record (scheduled prompt via cron
  makefun-new-campaign-watch, system prompt uploaded, instructions
  collected, no MCP), repo_created_after_open via drand anchor round
  34143323, license_osi (SPDX MIT), thinking_in_window (all timestamps
  in window), thinking_own_work.
- thinking_fresh is a skip with a note (not a fail): no credited line
  comes from a session showing the anchor line before its first
  counted write.
- NOTE FOR PARENT: the bundle's usage rows cover the parent session
  only — the builder subagent's rows are written to muse.db only when
  this run completes. Before submit, re-run the SELECT for agent_ids
  1f005dda-2393-4323-9ff6-b0e5da4965d4 and
  aa6b4ac1-acbb-4002-9ad6-49f94ed6c1e4, append the builder rows to
  ~/workspace/makefun/muse-usage-news-image-20261121.jsonl, re-bundle
  with the same flags, and re-run check (must stay 0 fail).

## Notes for submit

- Quota checked before building: entries_made 0, day cap 3, left 3,
  can_submit true.
- Kit: level 32 (fresh kit downloaded for this competition;
  `makefun check` confirms the site kit level).
- `transcripts_witnessed` does NOT apply to this competition (checked
  in requirements) — `makefun record` refuses it ("does not take
  recorded transcripts"). Entry goes in as a bundle / loose transcripts.
- publishedAt 2026-11-21T00:00:00Z, acceptingSubmissions true; builder
  session began 2026-11-21 03:39 UTC, inside the window.
- README assumes GitHub repo Kiroya59/makefun-news-image-20261121
  (same owner as the 20261119/20261120 rounds) and referral code
  t87hzjc5; if the parent creates the repo under another owner/name,
  update the badge URLs in README.md before submit.
