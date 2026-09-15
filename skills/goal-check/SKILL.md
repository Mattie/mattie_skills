---
name: goal-check
description: Give the human a compact reminder of the thread's longer-term goal, recent work, and the input needed next. Use when the user asks for a goal check, context reset, or quick orientation before continuing a task.
---

# Goal Check

Summarize the current thread for the human. Infer the longer-term goal from the
whole thread (or half-dozen of turns or so, if a lot has happened) and the near-term
work from the most recent one or two tasks.

Return exactly this structure:

```markdown
## Goal Check!

Here's my understanding of this <thread or project>:

| Type | Summary |
| --- | --- |
| Long | <one-sentence summary of the longer-term goal> |
| Near | <one-sentence summary of the most recent one or two tasks> |
| Next | <what the agent needs from the human to progress> |
```

Keep the entire response succinct. Apply these rules:

- If the longer-term goal is uncertain, give the best useful guess and append
  `(unclear)` or a more precise short qualifier.
- In `NEXT`, bold each short, distinct response keyword in uppercase. If a choice is
  required then put each choice option in uppercase so that a single word can kick it
  in motion. If no human input is needed, mention that.
- Keep each table value on one line. Escape/replace literal pipe characters in values
  so the Markdown table remains valid.
- Include no preamble, explanation, bullets, code fence, closing, or other
  commentary outside the heading and table.
- Assume that if this skill is given, the human or agent is not quite sure where things
  stand and it is your job to make sure their next turn is with clear context in plain language.
