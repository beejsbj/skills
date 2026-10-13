# Voice transcripts and consent

Travel and timezones no longer need cron conversion: the journal engine evaluates schedules in the timezone set in `journal.json`.

## Voice transcription provenance

Telegram voice notes are generally downloaded as audio and transcribed by Hermes's configured STT provider before the agent sees them. The journal engine stores the available transcript verbatim, but agents should preserve the epistemic layers:

1. Audio: what Burooj actually said.
2. STT transcript: the speech model's estimate, potentially wrong around names, code-switching, accents, and background noise.
3. Rose's annotations: interpretation of that estimate.

When asked how a note was transcribed, inspect the active configuration and logs rather than guessing. Report provider, model, local-versus-cloud processing, duration/language confidence when available, and whether Rose received raw audio or only injected text. Never silently repair uncertain proper names in the raw entry.

## Third-party recordings and consent

Recording, private retention, AI processing, and human/public sharing are separate permissions. Do not treat consent to one as consent to all.

A useful pattern for preserving unguarded presence is standing consent established beforehand, with an easy pause/delete option, plus renewed consent after unexpectedly intimate disclosures and separate consent before AI processing or sharing. Without consent, suggest an immediate first-person voice memo afterward: it preserves atmosphere and personal recollection without capturing another person's actual voice or disclosures.
