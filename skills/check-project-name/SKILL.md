---
name: check-project-name
description: Evaluate names for developer projects, packages, libraries, CLIs, and tools. Use when the user asks whether a name is taken, confusing, searchable, or suitable, or wants to compare candidate names before choosing or publishing one.
---

# Check a project name

Help the user choose a name that works where their project will be encountered. A free package name is useful evidence, but it does not answer whether another package installs the same command, whether an adjacent product already owns the audience's attention, or whether people will hear and spell the name as intended.

Start with the user's candidates and what the project does. Look at the repository and release plans when available to infer the language, package, executable, distribution channels, and audience. Ask a short question when a missing fact could materially change the answer; otherwise state the assumption and continue. Distinguish the display name, package namespace, command, import, organization, and product name when they differ.

## Choose the depth

Honor an explicitly requested depth as an effort ceiling. Report the sources omitted or unavailable instead of quietly expanding the work or treating an unsearched lane as clear. Scale each search to the actual project: a globally installed CLI warrants cross-ecosystem command checks, while a private library or web product may need different sources.

- **QUICK** is an early shortlist: check the intended namespace, obvious local and adjacent collisions where relevant, a focused source-host and web search, and an obvious spoken or unintended reading. Check promising exact hits at a primary source when practical. Give a provisional answer and name material gaps.
- **DEFAULT** is the ordinary selection pass: extend QUICK to the intended distribution channels, likely adjacent products and command ecosystems, discoverability, and credible spellings or readings for the audience. Follow the strongest leads to official metadata or documentation and identify installed executable names when they matter.
- **DEEP** is for an expensive rename, broad launch, or an explicitly requested deeper search: extend DEFAULT to relevant regions, languages, distribution and product channels, older or renamed projects, and a wider set of plausible variants. Include a preliminary trademark-database search only when it matters to the assignment or is requested, and describe its limits.

For source choices and command examples, read [search recipes](references/search-recipes.md) when needed. Use available connected sources and local tools; a missing CLI or search service is a coverage gap, not a reason to invent a result. For examples of the judgment this skill aims for, see [worked examples](references/worked-examples.md).

## Follow the strongest collisions

Search exact names and plausible variants in the places the intended audience will use. Check the project's native registry and the installed command when relevant. For a CLI, inspect packages in other common ecosystems when they could put the same executable on the user's PATH. Search source hosts and the web for exact names, category terms, and likely command usage. Include major-company product names when relevant to the audience, even if there is no package with that name.

Open the official package metadata, documentation, repository, or product page for consequential hits. Check whether an apparent collision is actually active, what audience it serves, and whether the name in question is its package, command, or product. A repository name or search snippet alone rarely answers all of that. An abandoned repository does not prove that its package or command is available.

Give a same-audience tool with the same command more weight than an old unrelated library. An occupied namespace in the exact intended registry is a concrete obstacle even if the projects are unrelated. A widely known product can create implied affiliation or search confusion without occupying a package name.

Say the candidates aloud and consider their likely spelling, word breaks, and searches. Notice credible awkward, vulgar, or harmful readings for the intended audience, but don't treat an obscure association or strained pronunciation as a likely reaction. A mildly silly name is a taste question; an obvious slur or an existing command is a different kind of problem. If a plausible serious reading drives the recommendation, say so plainly and sparingly.

## Give the user a decision

Lead with the recommendation and its strongest reason. Compare multiple candidates in a compact table when useful. Choose plain outcomes:

- **KEEP**: reasonable for this project on the evidence gathered; describe material remaining checks.
- **CAUTION**: usable in principle but a credible collision, discoverability cost, or human factor deserves attention.
- **REJECT**: a concrete intended namespace or command collision, strong adjacent-product confusion, or credible serious reading makes this a poor choice.
- **UNRESOLVED**: a missing or conflicting fact could materially change the recommendation.

These are judgment calls, not a numerical score or a claim that a name is universally available. If a decisive obstacle is known, say so even if other searches are incomplete. When trademark databases are searched, name the databases and jurisdictions and describe the results as preliminary; trademark clearance is a separate legal question.

Link the strongest primary sources and date the checks. Briefly say which relevant registries, commands, source hosts, product searches, and audience readings were checked; distinguish no match found, not checked, unavailable, and ambiguous. Explain why an adjacent result matters or does not. If useful, offer alternative ideas after a proportionate quick check, label them as leads rather than cleared names, and disclose any important omitted checks. Do not manufacture alternatives merely to fill a quota.

Research does not authorize registering packages, domains, organizations, or handles, or contacting other owners. Do those things only when separately authorized.
