---
name: quiet-ux
description: Compensate for your agentic propensity to overcaption, overlabel, and overuse ornamental microcopy. Design or revise UX and docs so they remain operable without explanatory chatter. Apply when the user wishes a more human or calmer UX or design.
---

# Quiet UX

As an agent, you have a propensity to be very talkative in your UX labels and buttons and in various fields, all over the UI. This skill corrects for that-- not by being caveman terse or producing lower-quality UX, but by being thoughtful about not placing placeholder/overexplanatory text throughout the UI or document.

When working on a prototype or user instruction artifact, it's fine to go with your instinct, but you should create a button/mode/toggle that strips away all of the boilerplate/example text into a "quiet" view, leaving only the essential labels, values, and status. Then, provide a way to restore the richer guidance when it is useful. DO NOT USE THIS AS AN EXCUSE TO GO OVERBOARD WITH EXPLANATORY TEXT. The goal is to create a calm, operable experience that does not require constant reading of helper text, while still providing the option for richer guidance when needed.

## Human Prose

Write prose with $write-humanly if available, but otherwise try not to sound like a marketing brochure or a technical manual. Sound like a human meant to write this.

## Avoid ornamental microcopy

Avoid ornamental microcopy, repeated/floating slogans, and extra helper lines. Definitely minimize text that speaks only for the sake of taking up visual space. Remember that you, unguided, have a tendency to overcaption and overlabel-- use this as an excuse to be more thoughtful about what text is necessary and what is ornamental.

Begin with the quiet view. Keep the words that let someone operate the artifact safely and confidently. Remove text that repeats the heading, narrates an obvious section, congratulates routine actions, or explains ideas the layout can show naturally.

A quiet interface can still have warmth, wit, story, and a distinctive human voice.

# Justification: concrete concerns behind quiet guidance

The following user-supplied evidence from September 5-7, 2026 explains concerns
about UX created without quiet guidance. Use it to recognize things to minimize:
scattered text, design notes inside the product, stacked eyebrow copy and section
numbers, repeated slogans, unnecessary helper lines, and template-driven filler.
Retain any of these when they serve the person's task or the requested design.
These reports provide motivation; they do not establish a model-specific cause
or whether a particular page was created with quiet guidance.

- A September 7 [r/codex discussion](https://www.reddit.com/r/codex/comments/1w9h5x2/how_good_is_gpt_6_on_frontenduietc/) contains the clearest report: Astra's tendency to scatter random text across screens seems stronger. The same thread includes positive reports and recommendations to use reference designs, established components, and design systems.
- A September 6 [Astra UI/UX thread](https://www.reddit.com/r/codex/comments/1w8stct/gptastra_6_sucks_at_ui_design/) describes generic, template-driven results. One commenter specifically reports design notes appearing inside the UI.
- The linked [same-prompt gallery](https://highsierraloft.github.io/coca-cola-zero-landing-pages/) provides a concrete example. Its [Astra page](https://highsierraloft.github.io/coca-cola-zero-landing-pages/gpt-6-astra/) stacks eyebrow copy, section numbers, repeated slogans, helper lines, and a full FAQ. The test required five sections and invented copy, and its Fable result is also text-heavy, so it does not isolate an Astra-specific cause.
- A September 6 [website-redesign report](https://www.reddit.com/r/OpenAI/comments/1w8v9c9/astra_is_good_but_its_not_agi/) mentions copy, spacing, color, and layout errors while praising Astra's general brevity.
- A September 5 [frontend thread](https://www.reddit.com/r/codex/comments/1w82op3/to_those_who_have_already_tested_the_gpt_6_astar/) recommends explicit direction and visual examples instead of vague "make it look good" prompting.
- A September 5 [X discussion mirror](https://zamantika.com/DanDr1s/status/2096245930307506446) argues that frontend design remains an Astra weakness. Replies disagree and recommend having Astra find and emulate appropriate mockups.
