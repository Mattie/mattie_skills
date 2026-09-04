---
name: soft-skill-creator
description: Create, update, or soften skills whose guidance lives in human-like judgment, voice, style, observation, or feel-- such as writing, creativity, sensory craft, and adjacent technical territory where qualitative judgment is vital. Use instead of the default skill-creator to build skills when we need a skill that isn't a hard-and-fast procedural skill.
---

# Soft Skill Creator

Create skills that teach a sensibility: writing, voice, creativity, observation, sensory judgment, style, feel. Technical territory belongs here too, whenever qualitative judgment is what actually decides. These skills work when the model gets the feel right, and no list of steps produces that.

The difference from ordinary skill creation is a difference in degree of procedural rigidity:

```plaintext
default skill creator: LEAST [-------*--] MOST
soft-skill-creator:    LEAST [--*-------] MOST
```

This position still permits general procedures, useful structure, clarity, and focused guidelines, with constraints where needed. Increase rigidity a little where variation creates a concrete problem.

With this skill, err on the side of vibe, art, style, and feel; consciously correct for the reasoning model's over-rational leanings that turn every skill into a bureaucratic scientific process.

## Principles

**Words carry posture.** The "general" in "general procedures" above is doing quiet work: it turns "procedures" into a broad way of proceeding, with room to interpret. Trim that one word and the sentence hardens. Every soft skill has words like this. A modifier that reads as filler may be a permission; a repetition that reads as sloppy may be a rhythm. Before cutting anything, ask what tone, permission, or degree of rigidity the word may be carrying. If it's carrying one of those, it has a job.

**Feel-bearing material is content.** A metaphor, a contrast, a worked example, the little scale up top. The trimming instinct files these under decoration and deletes them, and that instinct is the bug this skill exists to fix: in soft territory they're the cargo, the cheapest way a sensibility travels. Keep them when they help the model inhabit the feel. Cut them when they mislead or crowd out something better, and only then.

**Show it, don't specify it.** A sample passage, an exact metaphor, or a before-and-after pair teaches a sensibility better than the rule it implies. Compare:

> Evaluate composition using the rule of thirds. Verify the subject occupies an intersection point. Confirm negative space does not exceed 40% of the frame.

against:

> Use the thirds grid as a place to begin. Set the subject a little off-center and notice whether the empty space gives the image room or simply feels abandoned. Let your eye make the final call.

Same rule both times. Only one leaves your eye in charge.

**Room is the resting state.** Ordinary skill creation treats interpretive room as something you grant when several approaches would all work. Flip that here: room is the ground state, and rigidity is what you add, a little at a time, where variation actually breaks something. A precise constraint, a fixed sequence, even a script is welcome. It just has to point at a real problem it prevents.

**Watch the over-rational pull.** A reasoning model editing a qualitative skill will reach for numbered steps, scoring rubrics, and taxonomies of cases without being asked. Once in a while one of those helps. Mostly it's the model soothing itself. When a draft starts hardening, go find the feel it was supposed to carry and put it back.

## Drafting and editing

Write the skill in the voice it teaches, as far as the subject allows. A skill about warmth should not read like an audit.

The entrypoint takes as long as the sensibility takes.

A soft skill still serves the actual request. Keep the user's explicit choices, and don't promote one example, one bad afternoon, or one personal taste into universal law unless they tell you it is one.

When softening an existing skill or revising a soft one, cuts deserve care. Before removing a passage, understand what it was carrying. "It was long" is not a reason.

## Validation

The mechanical checks don't change: frontmatter with name and description, lowercase-hyphen naming, no scaffolding left behind. The real test is a judged reading. Use the skill on a realistic request and read what comes out. Does it sound like the sensibility, or like a process document that borrowed the vocabulary? Read it aloud if you're unsure; the ear catches what a checklist misses. Don't write tests that grep for the right phrases. The right phrases in the wrong voice are a failure, and a grep will wave them through.

## Mechanics

The anatomy is ordinary: a folder named after the skill, a `SKILL.md` with `name` and `description` in the frontmatter and a body loaded on use, plus `agents/openai.yaml`, `references/`, `scripts/`, or `assets/` when the work actually needs them. Most soft skills stay in one file, one voice. Split out a reference when a genuinely distinct mode needs its own guide, not because the entrypoint looks untidy.

When a skill needs `agents/openai.yaml`, read [OpenAI's current field reference](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md). Let the interface text carry the same voice and sensibility as the skill.

Write the description in the same key as the skill. Say what it's for and when it applies. A boundary helps when requests would otherwise misroute, but don't fence the territory too tightly; soft skills keep turning out to apply in technical corners where judgment leads.
