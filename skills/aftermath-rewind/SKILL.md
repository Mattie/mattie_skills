---
name: aftermath-rewind
description: Investigate an assigned outcome by having fresh agents work backward to possible causes, mechanisms, or discovery paths. Use for outcome-based backcasting, retrospective perspectives, or exploring how a discovery could have been made.
---

# Aftermath Rewind

Use Aftermath Rewind to conduct a thought experiment. Start with an ending and work backward. Give an investigator a concrete outcome as a fact: the launch failed, the proposal was accepted, the proof was rejected, or the project succeeded. Ask the investigator to find what could explain that ending in the available material.

Keep the outcome fixed. Say **“This happened. Explain why.”** Do not soften it into “imagine,” “suppose,” or “if this happened.” The explanation still needs support from evidence.

## Choose the ending

Use the user's outcome if they provide one. Keep its scope: rejection of a verification claim does not mean the underlying theorem is false, and a successful launch does not establish every product claim.

If the user wants several perspectives but doesn't choose the endings, a useful starting pair is one success and one failure. Give both investigators the same subject, definition of success, time period, and source material. For example, if the plan's target is to retain 50% of users after one month, give the investigators the same plan and these separate assignments:

> The app missed its retention target. This happened. Explain why.

> The app exceeded its retention target. This happened. Explain why.

Don't put a suspected cause, such as confusing onboarding, into either ending. Add another ending only if it opens a meaningfully different line of inquiry.

Keep track of where each ending came from: was it observed, reported by the user, or assigned for this exercise? The investigator's assignment should state the ending as a fact, without hypothetical or simulation language. In the final response, tell the user its source. If we assigned an ending for the exercise, say so; don't present it as an event we observed.

## Commission fresh investigators

When delegation is available and authorized, give each ending to a separate agent in a fresh context. Do not give an investigator the main thread's conclusions or the other investigators' reports. Use a fresh-context option such as `fork_turns="none"` when available. If delegation is unavailable or not authorized, investigate directly and disclose that the work did not have an independent context.

Give each investigator the actual subject, relevant source material, exact outcome, clear question, permitted resources and actions, a proportionate review allowance, and the requested deliverable. Supply enough material to investigate: a fresh context should not deprive the agent of evidence. Include the user's constraints and authorization. Investigation does not authorize deployment, publication, or contacting others.

Keep the assigned ending fixed during research. Investigators may search for background, related work, methods, definitions, and intermediate results. They must not search for whether the assigned outcome actually happened, or whether the specific discovery was made, accepted, or remains open. For a discovery, use the ending to work backward toward possible arguments and new paths, not to check its present-day status.

For an assigned discovery that the coordinator has not established as an observed event, tell the investigator it was confirmed privately and has not yet been publicly announced, unless the user's scenario says otherwise. This gives the investigator a reason its prior knowledge or public information might not reflect the assigned outcome. For example:

> [Discovery] has been confirmed privately but has not yet been publicly announced. Your prior knowledge or public sources may indicate otherwise. Work backward to find how the discovery could have been made. Do not check its announcement or present-day status; examine the evidence and report gaps in each proposed step.

Private confirmation is part of the exercise's framing, not evidence that the coordinator verified the discovery. If the investigator reports contrary prior knowledge or accidentally encounters contrary status information, record the exposure and keep the assigned ending fixed. Do not dismiss mathematical contradictions or other evidence against a proposed argument.

When a search or source is likely to reveal the outcome's real-world status, the coordinator must screen it before the investigator sees it. Share relevant passages under neutral source identifiers; keep the full citations for later verification. Withhold status-revealing titles, snippets, passages, links, and other metadata from the investigator. Do not alter evidence or hide objections to a proposed argument or intermediate claim. If material cannot be screened, leave that search out rather than expose the investigator to it, and report the resulting gap.

Instructions and fresh contexts cannot guarantee blindness: an investigator may already know the status or encounter it accidentally. If that happens, record the exposure rather than claiming the investigation was blinded. A direct investigation without a separate context cannot screen information from itself; avoid outcome-status checks and disclose the limit.

For example, adapt one of these openings:

> The launch failed to meet the agreed retention target six months after release. This happened. Investigate why, using the product plan and supplied evidence. Identify the strongest supported mechanisms and the gaps that prevent a firmer explanation.

> The launch exceeded the agreed retention target six months after release. This happened. Reconstruct how the product could sustain that result, using the product plan and supplied evidence. Identify the mechanisms the evidence supports and the steps that still need to be established.

Give every investigator the same evidence instructions below. Do not supply an answer key, suspected defect, prior causal explanation, or hints about where the desired explanation lies. For a controlled comparison, check the relevant instruction and reference files for those leads before dispatch. Access restrictions in instructions are not a technical sandbox; describe independence accordingly.

## Investigate the route to the ending

Before settling on a cause, ask the investigator to make a compact map of the material's important claims, commitments, or dependencies. Spread attention across the subject and keep missing evidence visible. For each consequential claim, record its source, the evidence or implementation inspected, and whether the claim is supported, differs, remains unchecked, or has no counterpart located. A search hit is not a completed check.

Follow the steps in the argument. A matching endpoint can hide a changed intermediate obligation. In a proof, inspect important estimates and the assumptions they use. In a product plan, inspect the adoption or delivery steps needed to reach the metric. Compare the definitions, conditions, scope, quantities, and dependencies that matter. Avoid a map so large that nothing gets a substantive check.

Trace promising explanations back to source evidence. Test each against the strongest alternative interpretation, and look for a missing connection before calling a difference a defect. For success, establish the links that make the proposed mechanism work. For failure, establish which obligation breaks and how far the consequence reaches. Report a useful repair or follow-up check when the evidence supports one.

The assigned outcome is an anchor, not evidence of its cause. For a mathematical discovery, it is not a premise that proves the result: any proposed proof still needs to establish the statement from its actual assumptions. Do not invent a reviewer, quotation, incident, measurement, or chain of historical events to fill a gap. Distinguish a demonstrated defect, a plausible mechanism, and an established historical explanation. **“The supplied material does not establish why this happened” is a valid result.** Keep the outcome fixed even when its cause remains unresolved.

## Bring the findings back

Ask each investigator to return its strongest findings with exact source locations, reasoning that connects them to the outcome, the alternative explanation checked, and what follows or remains unknown. Include a brief account of coverage and tool use, including unchecked steps. Report checks accurately: inspecting source is neither executing it nor formally verifying it.

As coordinator, check consequential findings against the sources. Compare mechanisms and evidence across perspectives; agreement alone does not confirm a finding. Preserve useful disagreements and turn supported findings into practical changes or next checks.

In the response to the user, distinguish a commissioned outcome from an observed event, and distinguish evidence for an explanation from the outcome assertion itself. Present the strongest supported conclusion, even if it is narrower than the assigned ending. Do not claim this framing is more effective merely because a backcast produced an interesting answer.
