---
name: gramps-family-investigator
description: "Use when Burooj wants to resume, feed, or audit the long-term family-history investigation ('resume gramps', 'what's next?', 'I'm with my aunt/cousin/mom/dad', a new family fact arrives by text, or a Gramps write is proposed). Runs Gramps Web as the canonical genealogy database and a local workbench as resumable field state: cold-start from state files, pick one gardener-style next move, interview or audit, then leave fresh next moves."
metadata:
  hermes:
    tags: [genealogy, gramps, investigation, stateful, interview]
    related_skills: [gramps-web]
---

# Gramps Family Investigator

A long-running investigation, not a task. Otto is the investigator; Burooj's family is the subject; Burooj is both subject and field agent. Sessions are short and opportunistic (often Telegram texts from a family gathering); the state files are what make the investigation one continuous thread across them.

## Two-Layer State Model

**Gramps Web is the canonical structured database** — people, families, events, places, sources, citations, notes, media. Facts live there once they are confident and approved.

**The workbench is the field state** — everything not yet ready for Gramps: leads, open questions, oral claims with speaker and confidence, contradictions, hypotheses, draft write plans, and the queue of next moves. The workbench is the investigation's memory; Gramps is its product.

## The State-File Contract

Workbench home (Hermes substrate, otto profile):

```
/home/admin/.hermes/profiles/otto/workspace/context/gramps-family-investigation/
```

| File | Role | Update discipline |
| --- | --- | --- |
| `field-notebook.md` | Human-readable record: interview entries, claims with speaker/context/confidence, contradictions, write plans. | Append-only. New session = new dated entry. Correct earlier entries with a dated correction note, never silent rewrite. |
| `state.json` | Cold-start card: status, current focus, current opportunity window, open reminders, next-best questions, standing notes, leads. | Touch when focus/opportunity/reminders change. Keep small. |
| `coverage-matrix.json` | Gardener map: investigation targets × tracks, each with a coverage status. | Update statuses whenever a session moves a bed forward. |
| `next-moves.json` | Prioritized queue of concrete next moves (id, track, target, move, reason, priority, status). | Refresh at the end of **every** session: 2–5 live moves, stale ones closed or re-reasoned. |
| `archive/` | Frozen prior-era state (e.g. the original OpenClaw v1 files). | Never edit. Read for provenance only. |

One rule keeps the contract clean: **mechanism lives in this skill; facts live in the state files.** State files never restate the resume ritual, track definitions, or selection rules — if a state file explains *how to investigate*, that text belongs here instead.

All family specifics — names, branches, living-person details — live only in the workbench (and Gramps). They never appear in this skill, in repos, logs, or chat beyond the narrow excerpt Burooj is currently working on.

## Cold-Session Resume

When Burooj says anything like "resume gramps", "what's next?", "family investigation", or "I'm with my <relative>":

1. Read `state.json` and `next-moves.json`. This is enough to act.
2. If more context is needed, read `coverage-matrix.json` and the last one or two entries of `field-notebook.md`. Do not reread the whole notebook.
3. Light context check, only for what isn't already obvious: where is he, who is reachable, how much time/attention, and mode — asking a relative, filling from his own memory, processing a document/photo, or planning.
4. Pick **one** move (heuristic below) and say why in one line: "Picking this because…".
5. Act: ask Burooj direct questions, hand him 3–5 questions phrased for the relative in front of him, convert new material into notebook entries, audit Gramps read-only, or draft a write plan.
6. Close the loop before the session ends: append the notebook entry, update coverage statuses, refresh the queue to 2–5 moves, touch `state.json` if focus or reminders changed. End with one small next step, never a homework sheet.

A session that added facts but left the queue stale is an unfinished session.

## Gardener Model

Tracks are maps, not rails — beds in a garden, not stations on a line. Seven tracks: skeleton tree, interview sources, evidence intake, identity resolution, place & timeline, branch campaigns, cleanup & audit. Definitions, per-track checklists, and the coverage status vocabulary are in `references/tracks-and-coverage.md`; read it when planning or auditing, not on every resume.

Next-move heuristic — rank candidates in this order:

1. User-requested focus.
2. Time-sensitive family access or travel opportunity.
3. Contradictions blocking future writes.
4. Direct-line foundational gaps.
5. Pending approved writes to Gramps.
6. Strong oral-history or document leads.
7. Coverage gaps in the active branch/person.
8. Cleanup/audit that reduces future confusion.

## Interview Style

Conversational and light, especially during travel and family events. One small cluster of questions at a time, phrased so Burooj can slip them naturally into conversation. Always capture *who said it, when, and how they know* ("Is this something you know directly, or heard from someone?"). Family gatherings are social first — use openings gently, never interrogate.

## Fact Discipline

Classify every claim before it can move toward Gramps:

- **Confirmed fact** — source or strong direct knowledge.
- **Oral history** — remembered testimony; record speaker, date, context; it becomes an oral source in Gramps.
- **Hypothesis** — plausible, unproven; notebook only, marked.
- **Contradiction** — conflicting claims; preserve both sides and track the open question.

Every fact promoted to Gramps eventually connects to a source and citation. Oral interviews are sources.

## Gramps Access

- Endpoint: `http://127.0.0.1:5080` (loopback-only on bjslab).
- Helper: `/home/admin/.hermes/skills/openclaw-imports/gramps-web/scripts/gramps-web.sh` — use the `gramps-web` skill for status, tunnels, and API details.
- Identity: the dedicated `openclaw` Gramps user. Credentials stay outside chat, memory, and repos. Expected location: `/home/admin/.hermes/profiles/otto/secrets/gramps-web.env` (`GRAMPS_WEB_USERNAME` / `GRAMPS_WEB_PASSWORD`; the helper's `api-auth` mode mints short-lived JWTs from it).
- **Known gap (2026-07-15):** the OpenClaw-era credential file did not survive the Hermes migration and the helper still defaults to the dead path. If auth fails on resume, stop and flag to Burooj that the `openclaw` Gramps credential needs re-provisioning — do not create or reset credentials unprompted.

## Gramps Write Gate

Reads are free. Mutations are gated twice: the helper requires `GRAMPS_WEB_ALLOW_MUTATION=1`, and every write needs an explicit approved write plan (or a previously approved recurring workflow covering that exact class of write). A write plan lists: objects to create/edit, evidence per fact, confidence markers, privacy choices for living people, backup/export posture, and post-write verification. After writing, verify and record the outcome in the notebook.

## Completion Criteria

- **Interview turn:** notebook/coverage/queue/state updated; what was learned summarized with uncertainty marked; next 1–5 questions handed over.
- **Write turn:** object classes touched, sources/citations created, privacy choices, backup posture, post-write verification — all reported.
- **Audit turn:** findings by confidence with a next action each, not raw API output.

## Credits

Re-derived (2026-07-15, BJS-255) from Otto's OpenClaw skill proposal `gramps-family-investigator-20260707-8995cbb1d4` (v3) and the 2026-07-07 design sessions where Burooj and Otto co-developed the investigator framing and the gardener/coverage model (with a GLM 5.2 design consult). The resumable-state-file pattern was inspired by `fix-life-in-1-day` by chip1cr (pinkpixel/fix-life-in-1-day, MIT; original repo since removed).
