# Reuse Shortlist Response Format

Use this format for default and deep Prior Art results. The research may remain
technical and rigorous; the response should help someone quickly decide what
existing work is useful, how much effort it saves, and what it brings with it.

## Response shape

1. Open with one or two sentences that summarize what the search found and
   identify the strongest lead.
2. Present the strongest candidates in a Reuse Shortlist table.
3. Follow the table with **What I'd do**, which gives the overall recommendation
   and sequence.
4. Close with a compact **Search note** describing coverage, confidence, and
   meaningful gaps.

Keep the opening, recommendation, and search note outside the table.

## Fit scale

Fit belongs to one candidate at a time. It rates expected practical leverage
after integration work, active constraints, incompatibilities, licensing,
maintenance, and risk are taken into account.

- **GREAT:** Covers nearly everything we need and can be used with little work.
  Expected leverage is high.
- **GOOD:** Covers a substantial part of the need and can be made useful with
  reasonable adaptation. Expected value clearly outweighs the added work.
- **PARTIAL:** Provides meaningful pieces or capabilities. We can use some of
  it or combine it with other tools, though substantial gaps remain.
- **WEAK:** Offers narrow or indirect value, such as ideas, test patterns,
  notes, or data. Expected payoff is low after adoption and integration costs.
- **BAD:** Provides no practical value under our constraints, or its cost,
  risk, incompatibility, staleness, or distraction outweighs its usefulness.
- **UNCERTAIN:** There is insufficient reliable information to judge its
  value. More research could materially change the rating.

`UNCERTAIN` is an ungraded evidence state; it does not rank below `BAD`.
Artifact type or age alone does not determine fit. Tests, notes, data, or an
older implementation may rate highly when they provide substantial practical
leverage for the actual problem.

## Candidate selection

- Rank candidates by practical usefulness under the actual constraints.
- Normally shortlist `GREAT`, `GOOD`, and `PARTIAL` candidates.
- Include a `WEAK` candidate when its indirect value informs the recommendation.
- Include a `BAD` candidate only when it is a prominent red herring or showing
  its rejection prevents repeated investigation.
- Include an `UNCERTAIN` candidate when it is a credible lead and a specific
  additional check could change its value.
- If no candidate has useful or explanatory value, say that none made the
  shortlist and omit the empty table. Still provide **What I'd do** and the
  **Search note**.

## Table columns

| Column | Required content |
|---|---|
| **Existing solution** | A short, hyperlinked candidate name followed by its license and adoption status. For each third-party adoption candidate, link immutable license evidence and the evaluated revision or content-addressed artifact. Include revision details for standard-library or repository-local candidates only when they materially affect confidence or reuse. |
| **Good&nbsp;fit?** | One bold fit label: `GREAT`, `GOOD`, `PARTIAL`, `WEAK`, `BAD`, or `UNCERTAIN`. |
| **Overview** | A factual description of what the candidate contains or does. |
| **Reusable parts / Savings** | Begin with what we can directly reuse. Follow with a separate `**Saves:**` paragraph explaining the work avoided or capability gained. Keep savings qualitative unless a time or cost estimate has supporting evidence. |
| **Work needed / Catches** | Begin with the work required to make the candidate useful. Follow with a separate `**Catch:**` paragraph for its main limitation, risk, or constraint. |

## Markdown template

```markdown
I found [plain-language summary]. [Name the strongest starting point and why it stands out.]

| Existing solution | Good&nbsp;fit? | Overview | Reusable parts / Savings | Work needed / Catches |
|---|:---:|---|---|---|
| **[Short candidate name](primary-source-url)**<br>[License](immutable-license-url) · [adoption status] · [evaluated revision] | **GOOD** | [What it contains or does.] | [Parts we can reuse.]<br><br>**Saves:** [Work avoided or capability gained.] | [Work required to make it useful.]<br><br>**Catch:** [Most important limitation, risk, or constraint.] |

**What I'd do:** [Recommended candidate or combination, sequence, and remaining custom work.]

**Search note:** [Sources and evidence lanes checked, practical confidence, bounded mode when relevant, and unresolved gaps.]
```

## Recommendation and search note

**What I'd do** synthesizes the whole shortlist. State which candidate or
combination to start with, the order of use, directly reusable parts,
adaptation or integration, remaining custom work, any constraint that should
change, and the next research check when evidence remains insufficient.

The **Search note** states the important sources and evidence lanes checked,
practical confidence in the shortlist, and unresolved gaps. Mention the mode
when bounded scope affects interpretation. Summarize deep coverage here; show
the full deep ledger only when the user asks for it or omitted evidence would
materially affect reliance.

## Rendering rules

- Do not wrap the table in a Markdown blockquote. Wide tables can overflow the
  quote container and render incorrectly.
- Keep candidate link labels short. Put descriptive detail in **Overview**.
- Link candidate names directly to primary sources.
- Keep important license and adoption constraints visible.
- Show fit labels in bold. Do not repeat the full fit definitions in the
  response.
- Keep each table cell to two short paragraphs when practical.
- Use labels only for `Saves` and `Catch`. Let reusable parts and required work
  read as direct statements.

## Worked example

I found one clean, reusable D&D corpus and a few sources that could help us
expand it. The SRD dataset is the strongest starting point.

| Existing solution | Good&nbsp;fit? | Overview | Reusable parts / Savings | Work needed / Catches |
|---|:---:|---|---|---|
| **[D&D 5.2.1 SRD QA](https://huggingface.co/datasets/datapizza-ai-lab/dnd5e-srd-qa/tree/656d81fa82987d9286fd077f025e4b575db148f2)**<br>CC BY 4.0 · adoption eligible · revision linked | **GOOD** | 56 Q&A pairs with difficulty labels, source passages, and document offsets. | Cases, expected outputs, and provenance.<br><br>**Saves:** Writing the baseline corpus and tracing every answer back to the rules. | Convert it into snackerbench case YAML and add edition metadata.<br><br>**Catch:** Small and heavily focused on revised 5e rules. |
| **[OpenTriviaQA D&D](https://github.com/uberspot/OpenTriviaQA/blob/dcc1cdf36c2985ed5c849d1f2265c5041ffcdfb9/categories/video-games)**<br>CC BY-SA 4.0 · STUDY-ONLY · revision linked | **WEAK** | Roughly 20 identifiable D&D multiple-choice questions with answers and distractors. | Coverage ideas, distractor patterns, and answer structure.<br><br>**Saves:** Some exploratory work when designing equivalent licensed cases. | Write equivalent licensed cases and verify every fact.<br><br>**Catch:** Share-alike terms and weak source provenance prevent direct reuse under the active policy. |
| **[Dragon #117](https://pied.nu/dragon/files/Drmg117.pdf)**<br>Copyrighted · STUDY-ONLY | **WEAK** | 100 professionally edited 1e questions with an answer key and rulebook citations. | Coverage ideas, difficulty patterns, and question styles.<br><br>**Saves:** Some exploratory work when designing a historical-rules suite. | Write equivalent licensed cases or obtain permission.<br><br>**Catch:** Copyright limits direct reuse. |

**What I'd do:** Import the 56 SRD cases first. Use OpenTriviaQA and the
magazine quizzes only to identify missing topics, distractor patterns, and
difficulty levels for newly written cases.

**Search note:** I checked public datasets, GitHub, trivia APIs, historical
publications, and large web quiz collections. I did not find another
substantial D&D-specific corpus with both vetted answers and clear reuse rights.
