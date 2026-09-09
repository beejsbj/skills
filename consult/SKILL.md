---
name: consult
description: Consult an independent model for judgment and reconcile its investigation with the evidence. Use when the user requests a second opinion, asks a named model for design, architecture, diagnosis, or review judgment, or another skill requires independent judgment; routine delegation and implementation stay with worker workflows.
---

# Consult

Bring back an independent judgment, not another pair of hands and not automatic agreement. Independence always requires a fresh context; model diversity is a separate choice.

## Frame and dispatch

Name the decision, verdict, or uncertainty the consultant must address. Assemble the smallest seed packet that lets a fresh model begin cold: relevant artifacts, constraints, observed behavior, and the requested output. Keep the framing neutral. Include the root agent's conclusion only when the task is explicitly to critique it, and label it as a hypothesis.

Dispatch the consultation read-only unless the user separately requested delegated implementation. Tell the consultant to inspect the essential evidence itself, conduct the independent investigation needed to test the packet and uncover omissions, and return findings and reasoning that could change the decision. Broad candidate collection remains a search task; the consultant investigates only as far as its judgment requires.

The brief is ready when a fresh model can locate the evidence, investigate the question independently, and produce the requested judgment without inheriting this conversation.

## Route the consultation

An explicitly requested model and effort win, including when that model matches the root. Otherwise, inspect the live tool or harness catalog first, then use [`../acpx/profiles.json`](../acpx/profiles.json) for model taste. Availability is environment truth; the roster is not an availability cache. On bjslab, resolve `cockpit handbook bjslab capabilities/t3-code.md` before choosing a route.

Choose model class and reasoning effort separately. Default a bounded consultation to an available frontier judgment model at low effort. Raise effort when the ambiguity or stakes require deeper reasoning. Answer a request for another or smarter model with a qualifying model distinct from the root; report the limitation when none is available. Same-model consultation still uses a fresh context and discloses the overlap. Use a small or standard worker for extraction and mechanical execution, which is delegation rather than consultation.

Prefer the environment's native subagent mechanism when it advertises the requested model. When it does not, try one appropriate authorized fallback and follow its governing skill or handbook.

The dispatch is complete when the requested model and effort, fresh context, access to the essential evidence, independent checks, and an answer to the question are all present. Otherwise report the concrete inability to obtain the requested consultation after the preferred route and appropriate fallback. Do not recurse into consultations about the consultation.

## Reconcile

Verify the consultant's factual claims against the available evidence. Distinguish:

- conclusions supported by both the evidence and the consultant;
- useful disagreement or newly exposed tradeoffs;
- claims rejected after verification;
- uncertainty that still belongs with the user.

Return the consultant's verdict and the root agent's final judgment distinctly. A consultant informs the decision; it does not replace the user's authority or silently expand the task.
