# Source access

Read the shared rules below, then the entries selected in `SKILL.md`. These entries map recall clues to access routes; current tool help and the governing handbook own command syntax and access policy.

`SKILL.md` owns source inclusion. Access notes for proposed sources and follow-up routes below do not make them default search targets.

## Shared access rules

Prefer an available authenticated search/read connector. Inspect its tool schema to confirm scope, filters, pagination, and whether reads can mark items read. Choose a read that preserves source state. A source absent from the active tool list may still be discoverable through tool search.

On bjslab, run `cockpit handbook bjslab` and read its resolved router before using services or private tools. From that handbook:

- `workspace-map.md` and `service-map.md` locate Brain, Records, and chat-scrobbler.
- `capabilities/personal-data-tools.md` routes Karakeep and Google to their maintained runbooks and safe wrappers.
- `capabilities/macbook-ssh-access.md` governs reaching the Mac via `ssh macbook`.

On another host, use that environment's configured connectors, workspace map, and access guidance. Paths below are location hints, not a reason to create directories or cross hosts. Verify the selected path exists and read applicable local instructions before content searches. If no supported route exists, report the source unavailable and continue with another plausible source.

## Brain

Use for Burooj's own language: journal entries, reflections, synthesis, voice transcripts, reading notes, and personal ideas.

Known vault locations are `/mnt/server-ssd/BJsWorkspace/Brain` on bjslab and `/Users/burooj/BJsWorkspace/Brain` on the Mac. Read the vault's `AGENTS.md`. Start with likely filenames or subdirectories, then use bounded `rg` searches in Markdown for distinctive fragments and aliases. Open the matching section with enough context to identify authorship and date.

`Journal/` and `Voice Recordings/` can contain firsthand accounts; `Readwise/` contains imported material. Follow a clearly derivative note to its origin. Search relationship or health areas, including `Connections/` and `fallingout/`, only when the request points there. A vault-wide content query also touches those areas: choose or exclude directories before running it.

## Chat-scrobbler

Use for prior captured AI conversations. Prefer connected search tools, then retrieve the matching messages and nearby context. Establish speaker and branch: a suggestion, an abandoned branch, and an accepted decision are different evidence.

The bjslab CLI fallback is `/home/admin/.local/bin/chat-scrobbler`. Its known store handles are:

```sh
CANONICAL_DIR=/mnt/server-ssd/chat-scrobbler/canonical/sessions \
INDEX_PATH=/mnt/server-ssd/chat-scrobbler/index/sessions.db \
/home/admin/.local/bin/chat-scrobbler search "terms" --json

CANONICAL_DIR=/mnt/server-ssd/chat-scrobbler/canonical/sessions \
INDEX_PATH=/mnt/server-ssd/chat-scrobbler/index/sessions.db \
/home/admin/.local/bin/chat-scrobbler get "source:source_id" \
  --markdown --role user,assistant --text-only
```

Confirm supported options with the top-level `chat-scrobbler --help`. Its subcommands do not implement separate help; in particular, `list --help` performs a list operation. Use result limits and message-level retrieval if the current interface supports them. The session ID comes from a search hit. If only whole-session retrieval exists, fetch only a strong candidate and return the relevant excerpt; exclude reasoning and tool blocks unless specifically sought. Substitute search terms with safe argument quoting.

The known capture scope is browser conversations from ChatGPT, Claude, and Gemini; verify current provider coverage before claiming a harness or period was searched. Capture depends on what the extension encountered, so old unopened conversations may be absent. Lexical and semantic search have different coverage; record which was available. For Codex, Claude Code, T3, OpenCode, or Hermes history, use a documented transcript-search interface if available; otherwise report that gap. Recall is not authority to probe live harness databases or rebuild indexes.

## Karakeep

Use for intentionally saved resources, including titles, URLs, tags, notes, highlights, and archived text. On bjslab, the personal-data capability points to the Karakeep skill and `runbooks/karakeep-memos.md`; follow those for authentication checks and current CLI use.

Search title, URL, tags, and notes first with a small result limit. Fetch archived content only when those fields cannot identify the item or support the requested fact. Preserve the original URL and bookmark ID so an imported copy can be recognized. An archived article's claims belong to its author unless Burooj added commentary.

## GitHub and local repositories

Proposed addition. Use when the current request explicitly includes GitHub or a local repository, or to inspect a specific artifact linked by an included source.

Use for files, commits, issues, pull requests, reviews, and implementation chronology. In a known checkout, start with `rg` and relevant `git log` queries (`--grep`, `-S`, or `-G`); bound paths, dates, and output. Otherwise use a GitHub connector or authenticated `gh` search/read commands scoped to the likely owner or repository. Inspect current help for result limits and syntax.

Follow a remembered implementation claim to the relevant diff; follow a shipping claim to release or deployment evidence. Preserve commit IDs and stable issue/comment links. Public GitHub search can identify a candidate project, but personal provenance must come from a saved item, visit, conversation, contribution, or local record before calling it Burooj's remembered project. Keep private query context out of unrelated public search services.

## Linear and Cockpit

Use for project intent, decisions, issue state, and receipts. Cockpit's repository and handbook hold durable context and operational records; Linear holds issues, comments, and workflow history. Search the relevant Cockpit documents as well as the board when the topic could live in either. Read the `cockpit` and `linear` skills for their respective read routes. On bjslab, the governing board interface is `cockpit linear`; inspect its help for current and settled board searches and candidate issue reads. Include completed/canceled work when searching history. Current status alone does not establish what the status was at the remembered time; look for dated history or receipts.

## Gmail

Proposed addition. Use when the current request explicitly includes email.

Use for messages, promises, decisions, purchases, receipts, and attachments. Narrow the search by sender/recipient, phrase, subject, date, or attachment before retrieving a message. Cite message/thread IDs or safe links and distinguish sent time from dates described in the body. Retrieve attachments only when necessary to answer the question.

On bjslab, follow the Google route in the personal-data capability and `runbooks/personal-api-toolbox.md`. Use the secure `gog` wrapper with `--readonly --gmail-no-send --no-input` and structured, untrusted-content output as documented there. Inspect current `gmail search` help for query and limit syntax. Use the wrapper's authentication check rather than opening credential files.

## Calendar

Proposed addition. Use when the current request explicitly includes calendar records.

Use for event dates, invitees, locations, and planned sequencing. Select the likely calendar and a bounded date range; search across calendars only when the clue leaves the calendar uncertain. For recurring events, identify the relevant occurrence and its timezone rather than reporting the series start. Check cancellation or response status when relevant to the recollection.

On bjslab, use the same Google capability/runbook and read-only wrapper as Gmail. Inspect current `calendar events` help for calendar selection, date filters, query, and limits. Preserve the event ID and occurrence date in the evidence.

## Browser history

Use for a page visited without a known save. Reach the Mac only through the documented access route. On the Mac, these are conventional locations under `/Users/burooj/Library/`:

| Browser | Profile root and history file |
| --- | --- |
| Chrome | `Application Support/Google/Chrome/` — selected profile's `History` |
| Arc | `Application Support/Arc/User Data/` — selected profile's `History` |
| Firefox | `Application Support/Firefox/Profiles/` — selected profile's `places.sqlite` |
| Safari | `Safari/History.db` |

Resolve the browser/profile from clues or directory metadata; profile names are not durable identifiers. Exclude System and Guest profiles. When multiple personal profiles remain plausible, include that limit in the scout assignment rather than silently sweeping them all.

Use `/usr/bin/sqlite3 -readonly` with a narrow title/URL/date predicate and a small result limit. Inspect schema metadata before forming the query. Chromium joins `urls` to `visits`, Firefox joins `moz_places` to `moz_historyvisits`, and Safari joins `history_items` to `history_visits`; verify timestamp units and epoch before filtering or reporting dates. Quote both remote-shell arguments and SQL values safely. Return matching title, URL, and visit time only, omitting credential-bearing URL components.

Locks, WAL state, and macOS privacy restrictions can prevent reliable reads. Report the gap if the supported read fails; leave live profiles, permissions, and browser processes unchanged. Current or synced open tabs can supply a lead but are not a record of historical visits.

## Records

Use for official documents and identity-heavy evidence. Known locations are `/mnt/server-ssd/BJsWorkspace/Documents/Records` on bjslab and `/Users/burooj/BJsWorkspace/Documents/Records` on the Mac. Read local instructions, narrow by filename/document type, then extract the minimum fact from the relevant document. Prefer a locator over reproducing identity details.

## Domain homes

For a clue clearly belonging to a specialist system, load its skill or capability: `fiscal` for finances, `gramps-family-investigator` for family history, Cooklang Kitchen for cooking, and Trakt for watch history. Use its canonical records and read interfaces under the recall boundary in `SKILL.md`. Brain can explain personal meaning but does not replace those records.
