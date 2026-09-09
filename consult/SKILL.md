---
name: consult
description: Obtain an independent judgment from another model and reconcile it with the evidence. Use when the user asks to consult, get a second opinion, ask Astra or another named model, or when another skill needs independent design, architecture, diagnosis, or review judgment; exclude routine delegation and mechanical execution.
---

# Consult

Bring back an independent judgment, not another pair of hands and not automatic agreement.

## Frame the question

Name the decision, verdict, or uncertainty the consultant must address. Assemble the smallest evidence packet that lets a fresh model reason cold: relevant artifacts, constraints, observed behavior, and the requested output. Keep the framing neutral. Include the root agent's conclusion only when the task is explicitly to critique it, and label it as a hypothesis.

The brief is ready when the consultant can answer without inheriting this conversation or asking where the evidence lives.

## Route the consultation

An explicitly requested model and effort win. Otherwise, inspect the live tool or harness catalog first, then use [`../acpx/profiles.json`](../acpx/profiles.json) for model taste. Availability is environment truth; the roster is not an availability cache. On bjslab, resolve `cockpit handbook bjslab capabilities/t3-code.md` before choosing a route.

Choose model class and reasoning effort separately. Default a bounded consultation to an available frontier judgment model at low effort. Raise effort when the ambiguity or stakes require deeper reasoning. When the user asks for another, smarter, or named model, use a qualifying model distinct from the root model and report a blocker if none is available. Use a small or standard worker for extraction and mechanical execution, which is delegation rather than consultation.

Prefer the environment's native subagent mechanism when it advertises the requested model. When it does not, use an available harness route and follow its governing skill or handbook. Independence always requires a fresh context; disclose when an unqualified consultation must reuse the root model because no distinct model is available.

## Dispatch independently

Make the consultation read-only unless the user separately requested delegated implementation. Give it a bounded question, evidence locations, constraints, and a checkable response contract. Ask for findings and reasoning that could change the decision, including disagreement and missing evidence. Do not seed the desired answer or ask it to ratify the root agent.

The dispatch is complete when one qualified independent response has returned or every authorized route has produced a concrete availability blocker. Do not recurse into consultations about the consultation.

## Reconcile

Verify the consultant's factual claims against the available evidence. Distinguish:

- conclusions supported by both the evidence and the consultant;
- useful disagreement or newly exposed tradeoffs;
- claims rejected after verification;
- uncertainty that still belongs with the user.

Return the consultant's verdict and the root agent's final judgment distinctly. A consultant informs the decision; it does not replace the user's authority or silently expand the task.
