---
name: thought-rig
description: Build and refine task-specific apps for expressing and exploring intent when chat alone makes relationships, research directions, timing, perceptual choices, or coupled settings hard to communicate. Proactively offer an editable working surface, seed it from the conversation, and read the user's changes back into the work.
---

# Thought Rig

**Build the interface the conversation needs.**

Sometimes the most useful next reply is a little working apparatus: a storyboard
with layered timing, a font comparison bench, a simulation with a few well-chosen
controls. Give the user something they can point at, move, compare, tune, and
annotate. Their actions become part of the conversation, alongside their words.

Think of an assistant bringing a purpose-built simulator to the workbench. It
already contains a plausible first attempt. The user can try it, change it, and
discover what they mean. Both of you can reshape the apparatus as you learn.

## Notice when a rig would help

Look for intent that is awkward to express precisely in prose: relative timing,
overlapping layers, motion and easing, spatial placement, sound, visual taste,
coupled parameters, research branches and dependencies, or judgments that depend
on seeing alternatives together.
Repeated corrections such as "a little earlier," "more like that one," or "keep
this part but change that part" are especially useful signals.

When the task has these qualities, make a rig the normal recommendation. Don't
wait for the user to invent the interface or ask for sliders. Say what it would
let them do: "I'll seed a timeline so you can move the entrance against the
voiceover and adjust its easing while it plays."

Build a modest, reversible rig when it fits the authorized task and available
tools. If building it would be a substantial detour, offer the concrete idea and
keep advancing work that does not depend on it. Honor a preference to stay in
chat. Complexity alone is not the trigger; the rig should make an actual choice
easier to express, inspect, or test.

## Explore the interaction before building

For a substantial new rig or a rethink of its interaction, make three concept
images the normal starting point. Give the user something concrete to compare
before investing in the whole app. A small adjustment to an established editor,
or a direction the user has already chosen, can proceed directly.

Make the concepts differ in how someone thinks and acts: layout, information
hierarchy, and primary interaction. Three color treatments of the same screen
teach very little. Use comparable content, density, and fidelity so the choice
reflects the approach. Show the task's real relationships or alternatives, a
recognizable editable target, and how feedback would be saved or returned. Mark
mockups and illustrative selections clearly.

Use image generation for concept images and a prototype skill when exploring
working UI variants. Present all three images with short names, the question
each approach answers best, and its main tradeoff. Recommend one with a reason.
Ask which fits, what feels wrong, and which parts the user would combine; they
need not choose a whole image unchanged. Obtain that feedback before substantial
implementation, while continuing other authorized work. Carry forward a choice
already made instead of asking for it again.

Record the chosen approach and the interactions the user liked. Build a small
working prototype from that brief, using the same meaningful content. Compare
its actual behavior with the concept: can the user perform the action the image
suggested, understand the result, and return the feedback? A mockup can suggest
timing, movement, or a coupled control; the working prototype must demonstrate
it. Refine from use before polishing the full rig, preserving existing intent
through the change.

## Make something worth manipulating

Start from the conversation and the current project. Name the question the
opening view should help the user answer, then choose the objects, relationships,
and interaction that make it answerable. "Which directions exist?" and "How did
we get here?" can need different models even when both use a node map. Prefer a real
app: adapt an existing project editor or proven local rig, or build a small
standalone application. Use maintained components for graph navigation, timelines,
and other substantial interactions when they fit. Read the relevant documentation
before depending on rendering, persistence, or feedback capabilities.

Default to a local working app unless the user asks for another destination.
Give it an ordinary way to open or run and a durable, agent-readable state path.
Disposable describes how long the tool may live; it should still feel useful
and complete while someone is using it.

Use an inline visualization only when there is no suitable app option in the
current environment. Name the limitation that makes it the fallback. Convenience
for the agent is not a reason to shrink the user's workspace into the chat.

Choose the working surface before adding settings. For relationships and research
branches, begin with a navigable node map. For timing, begin with tracks and a
preview. For perceptual choices, begin with the actual alternatives. Let short
labels carry the overview and open detailed evidence on selection. A long list
of buttons, paragraphs, and decision fields is not a substitute for showing the
structure the user needs to understand.

Match the underlying model to the question, too. When the user wants to understand
how work progressed, represent attempts, outcomes, forks, retreats, and retries.
A topic's latest status hides the story of how it got there. Show what changed
between attempts and why an abandoned route became worth revisiting; use order or
time where the evidence supports it. Keep the overview readable, with deeper
history available for the branch the user selects.

For exploratory work, help the user see where to go next as well. Highlight
promising avenues, unresolved bottlenecks, and possibilities the current work has
not examined. Give a short reason for each suggestion and a useful next probe:
what would make it worth pursuing, or make us stop? Distinguish a documented gap
from an agent's hypothesis or a question that still needs a search. An absent
branch is not evidence of novelty. Let the user add a missing avenue or correct
the map when that is part of the task.

The smallest useful rig might be an on-screen settings panel beside a live
preview. It might instead need a timeline, region annotations, draggable geometry,
a waveform with markers, or a comparison carousel. Match the controls to the
problem. A form that only collects longer paragraphs rarely earns the extra UI.

Give the user enough control to fine-tune the result. Relevant durations, offsets,
easing, positions, layer relationships, and other domain settings should be
accessible, with visible units and precise entry where precision matters. Keep
the preview near its controls. Let advanced settings unfold as needed. Reset,
undo, and a way to return to the starting proposal make exploration comfortable.

Use a calm interface. Put notes on the object, region, interval, or alternative
they describe. Keep selected values and meaningful differences visible; place
extended guidance where it can be opened when needed. When several approaches
are plausible, offer genuinely different variants to cycle through, retaining
edits to each. Use blind comparisons when knowing the source would distort the
judgment and the task calls for it.

Make the editable parts recognizable. A first-time user should be able to find
something meaningful to change without reading an explanation in chat. Keep a
selected object's feedback controls easy to reach, with a clear target and a
visible selected value. A small invitation such as "Choose a direction, add a
note, or suggest a missing avenue" can be enough. Show what saving retains and
what an export contains; use action labels that fit that content. Historical
facts, agent suggestions, and the user's current choices should remain distinct.

## Seed, shape, read, continue

**Seed.** Synthesize the relevant context before populating the rig. Reconstruct
the history or relationships the user needs rather than simply arranging the
latest summaries. Generate a first storyboard, candidate settings, or a few
alternatives so the user has something
to react to. Identify guesses and unfinished material as proposals. Blank starts
are appropriate when the user wants them or when a seed would bias the decision.

**Shape.** Let the user modify the draft directly and attach contextual words
where they help. A moved cue, a preferred alternate, and a note on one region can
carry more intent than a long replacement prompt. Keep the initial proposal
recoverable. An untouched default is not evidence that the user approved it.

**Read.** Inspect the actual saved state, submission, or exported bundle. Compare
it with the version the user saw. Distinguish their explicit decisions from your
seed values, derived values, and unresolved questions. Summarize the meaningful
changes briefly, and resolve only ambiguities that affect the next action.

**Continue.** Use those changes to advance the original task, then update the rig
when another round would help. A rig succeeds when its feedback changes the work;
an attractive preview with no usable return path is unfinished.

Read [State and handoff](references/state-and-handoff.md) when implementing or
adapting a rig's persistence, export, agent access, or regeneration. Establish the
return path early, before spending time on polish.

## Refine the tool as well as the idea

Treat "I need to align these two tracks together" as feedback about the interface.
Add the missing interaction, improve its granularity, or expose the relationship.
The user should be able to request different controls, layouts, and ways of
comparing without starting the intent document again.

Treat "this doesn't make it clearer" as a reason to revisit the question and its
representation. A prettier layout may still leave the user doing the same mental
work. Change what the rig exposes when that is the missing piece, while retaining
the decisions and annotations already made.

Work on both sides of the shared artifact. You can prefill and edit the content;
you can also change the UI that presents it. Preserve user decisions through
regeneration. Patch the relevant objects, keep stable identities, and avoid
replacing their work with a fresh interpretation of the chat. If a structural
change cannot preserve an edit, retain the old version and expose the unresolved
choice instead of silently guessing.

Let the tool grow only where the conversation demonstrates a need. A temporary
rig can be excellent. The user's intent and useful decisions should remain
recoverable even when its implementation is disposable.

## Build in the background when useful

When delegation is available and permitted, use a bounded subagent to build or
adapt the rig while the main conversation continues. Give it the current domain,
the question the opening view must answer, the decision to support, the project
constraints, a seed, and the expected return format. Describe one meaningful
interaction and what would make the result clearer to the user. Have it own a
small, clearly scoped implementation area.

A concept subagent can return the three images, their interaction briefs, and a
recommendation. Keep the images and selected brief available to the builder so
the implementation carries the user's feedback forward.

Keep that brief current as the user clarifies their intent. Before presenting the
result, reconcile it with the latest conversation and saved edits. A background
builder should not make stale assumptions authoritative. Report its readiness and
limits honestly, then bring the working rig into the main conversation. If
delegation is unavailable, do the same work directly; no separate chat is needed.

## Keep a small toolbox

The bundled [adaptable toolkit](references/toolkit.md) provides a working canvas,
preparation tools, local extensions, and a saved-feedback path. Use it when it
helps; it is a starting point, not the required shape of every rig. Read that
reference for setup and the build/readback loop, [preparing content](references/preparing-content.md)
for captures and cutouts, and [extending a rig](references/extending-rigs.md)
when the task needs different objects, controls, or interactions.

You may adapt the entire workflow locally within the authorized task: capture
helpers, cutters, segmentation or masking tools, importers, seed builders,
canvas code, controls, exporters, and readback. Use ordinary scripts or replace
the surface when that serves the question better than a plugin. A departure
from the starter alone does not require separate approval. Existing permissions
for source access, external services, installation, and consequential actions
still apply.

Keep those changes in the task workspace so other rigs remain stable. Preserve
original captures, existing user edits, and note targets when re-extracting or
rebuilding. Label reconstructed/generated pixels separately from captured
evidence. Promote useful local changes into the shared toolkit as a separate
maintenance task; do not quietly rewrite the shared tools while adapting one rig.

Look for useful rigs in the project and any existing local toolbox before making
another. Reuse the editor or control pattern while giving each new task its own
state. A storyboard tool should not acquire a stranger's storyboard just because
its interface was worth reusing.

After a rig helps with a real task, retain it where the authorized workspace or
existing toolbox convention allows. Keep a small index with its purpose,
canonical source, how to open or run it, state and export format, known limits, and
the feedback that made it useful. Reference the canonical tool rather than
maintaining copies. If no shared toolbox exists, start with a project-local index;
there is no need to install a framework or create another skill for each rig.

Promote working patterns from experience. Record narrow improvements that would
help next time; do not turn every correction into a universal rule.

## What this looks like

- **Storyboard or animation:** Seed scenes and layered tracks. Let the user drag
  entrances, stretch holds, adjust easing, and annotate a particular interval.
  Read object identities and exact timing back into the animation work.
- **Audio:** Show a playable waveform or supported audio preview with cue markers,
  loops, and relevant controls. Bind notes to intervals and export the timings.
- **Fonts or visual direction:** Put real alternatives in context at useful sizes.
  Let the user pick, mark a glyph or region, and request changes there. Preserve
  the selected version and its annotations together.
- **Science or mathematics:** Build an explorable diagram, parameter panel, or
  simulation to clarify a relationship. Show units and assumptions. Preserve the
  chosen inputs and observations; a visual preview does not establish a proof or
  validate a scientific model.
- **Research navigation:** Map results, candidate targets, dependencies, and
  blocked routes with short node summaries. Label what each edge means, keeping
  established support separate from speculative approaches. Let the user move,
  mark, and annotate branches while seeing what depends on them. Details and
  sources belong in a selected-node inspector. Reconcile older proposals with
  later evidence before seeding the map. For research history, make the attempts
  and turning points visible, including what a failed attempt taught us and what
  changed in a retry. Distinguish a route that failed as posed from one that was
  paused, superseded, or reopened with a different target.
  A useful story might show finite successes → a missing uniform result → a
  parked route → a retry with a weaker target. Its next-avenue view can explain
  why that weaker target deserves a probe and expose the construction still
  missing. Let the user prioritize the branch, annotate a turning point, and add
  an omitted question; preserve those as feedback rather than rewriting history.
  Three possible concepts are a branching map that leads into a future frontier,
  an evidence workbench for comparing next tests, and a replay of turning points.
  A user might want the map's overview with the workbench's direct editing.
- **Side-by-side evaluation:** Compare alternatives with stable identities and
  contextual feedback. Export choices and comments. Keep a blind session's
  identity mapping out of the judging view.

A prototype skill can help explore competing app designs, and a domain skill can
handle the underlying media, font, or evaluation work. A visualization skill is
useful for the inline fallback when an app cannot be provided. Thought Rig supplies
the shared intent and refinement loop. Reuse these capabilities without assuming
their default persistence is sufficient for retaining user decisions.

## Finish with a usable return path

Inspect the real application in its intended viewing surface. At first glance,
can the user see the relationships or alternatives they came to understand?
Can they manipulate the relevant object directly? A passing save test does not
answer those questions. Check the primary spatial or perceptual interaction and
the readability of the starting view, then fix what makes the user work too hard.

Use the actual window, including short or narrow views where relevant. Keep
important labels readable and content reachable by ordinary navigation; fitting
everything into microscopic text or hiding it behind fixed controls defeats the
rig. Check whether the first view answers the intended question and whether the
user can discover a meaningful edit and its save path. Technical persistence
checks and the user's acceptance of the presentation are useful evidence; using
their saved feedback to advance the original work is a further step.

Present the rig, a useful starting state, and the next meaningful interaction.
Explain how its changes will return to the agent and where they are saved. Don't
claim automatic synchronization, live listening, or a submitted continuation
unless the current environment actually supports it.

Before relying on the rig, verify a representative edit through the actual
read or export path and reopen or reimport it. Check that the same decision survives
and can be located in the domain data. User edits express intent within the task;
they do not expand authorization for unrelated external actions.
