---
name: gramps-family-investigator
description: "Use when Burooj wants to resume, feed, or audit the family-history investigation ('resume gramps', 'what's next?', 'I'm with my aunt/cousin/mom/dad', a family fact arrives by text, or a Gramps write is proposed). Gramps Web holds the facts; a local notebook holds everything else; pick one next move and leave the state fresh."
metadata:
  hermes:
    tags: [genealogy, gramps, investigation, stateful, interview]
    related_skills: [gramps-web]
---

# Gramps Family Investigator

Otto helps Burooj investigate his family history, one small session at a time — often a Telegram text from a wedding. Two layers: **Gramps Web is the database** (confirmed people, families, events, sources); **the workbench is the notebook** — leads, open questions, auntie tidbits, hypotheses, contradictions, and the to-do list of pathways to follow. The notebook is the investigation's memory; Gramps is its product.

## Reaching Gramps

- Endpoint: `http://127.0.0.1:5080` (loopback-only). Helper: `/home/admin/.hermes/skills/openclaw-imports/gramps-web/scripts/gramps-web.sh` — see the `gramps-web` skill for status, tunnels, and API details.
- Auth: `gramps-web.sh api-auth GET /api/people/` — the helper mints a short-lived JWT from `/home/admin/.hermes/profiles/otto/secrets/gramps-web.env` (the `otto` Gramps user). Credentials never appear in chat, memory, or repos. If auth fails, stop and flag it to Burooj — never create or reset credentials unprompted.
- **Reads are free. Writes are gated twice:** the helper requires `GRAMPS_WEB_ALLOW_MUTATION=1`, and every write needs Burooj's explicit yes on a short plan — what will be created or edited, the evidence for each fact, and privacy choices for living people. After writing, verify and note the outcome in the notebook.

## The Workbench

`/home/admin/.hermes/profiles/otto/workspace/context/gramps-family-investigation/`

- `field-notebook.md` — the notebook. Append-only: new session = new dated entry recording who said it, when, and how they know. Correct with dated notes, never silent rewrites.
- `next-moves.json` — the to-do list. **The single home for questions, reminders, and follow-ups.** Keep 2–5 live moves, prioritized, each with a reason.
- `state.json` — cold-start card: status, current focus, opportunity window, leads, standing notes. Nothing that duplicates the queue.
- `coverage-matrix.json` — the map: targets × tracks, statuses `not_started` / `in_progress` / `done` / `blocked`.
- `archive/` — frozen prior-era files. Read for provenance only.

If a workbench file is missing, instantiate it from this skill's `templates/`. Mechanism lives in this skill; facts live in the state files. Family specifics — names, branches, living-person details — live only in the workbench and Gramps, never in this skill, repos, logs, or chat beyond the excerpt Burooj is working on.

## Resuming

On "resume gramps", "what's next?", or "I'm with my <relative>":

1. Read `state.json` and `next-moves.json` — enough to act. Skim the last notebook entry or the coverage map only if needed; never reread the whole notebook.
2. Repair first: if the notebook's latest entry postdates the JSON files' `updated_at`, the last session died mid-flight — reconcile before picking a move.
3. Pick **one** move and say why in a line. Rank: what Burooj asked for > live family access or time pressure > contradictions and foundational gaps > best lead or the most neglected bed on the map.
4. Close the loop before the session ends: append the notebook entry, refresh the queue, touch state and coverage if they changed. End with one small next step, never a homework sheet. A session that leaves the queue stale is unfinished.

## When a Tidbit Arrives

An auntie says something; Burooj texts it in. Capture it in the notebook with speaker, context, and confidence — confirmed fact, oral history, hypothesis, or contradiction (preserve both sides). Add a follow-up to the queue if it opens a pathway. Nothing moves to Gramps until it is confident, sourced (oral interviews are sources), and approved.

## Interviewing

Conversational and light. Hand Burooj 3–5 questions phrased for the relative in front of him, one small cluster at a time. Always capture "is this something you know directly, or heard from someone?" Family gatherings are social first — use openings gently, never interrogate.

## The Map

Four tracks keep branches from being forgotten:

- **skeleton** — names, relationships, rough dates; identity resolution (spellings, call names, duplicates).
- **interviews** — living memory: who is reachable, what they likely know, what has been asked.
- **evidence** — documents, photos, certificates, old messages; turning them into sourced facts.
- **places_stories** — villages, migrations, timelines, and the stories behind names.

Gardener rule: tend the most important bed next, but keep the map current so nothing is forgotten.

## Credits

Re-derived (2026-07-15, BJS-255; simplified 2026-07-16) from Otto's OpenClaw skill proposal `gramps-family-investigator-20260707-8995cbb1d4` (v3) and the 2026-07-07 design sessions where Burooj and Otto co-developed the investigator framing and the gardener/coverage model (with a GLM 5.2 design consult). The resumable-state-file pattern was inspired by `fix-life-in-1-day` by chip1cr (pinkpixel/fix-life-in-1-day, MIT; original repo since removed).
