# Worked examples

The short cases below are synthetic: they illustrate how to reason from supplied evidence and make no claims about actual names or current availability.

## Free package, occupied command

A developer wants to ship a CLI as `larkspur` on crates.io. The exact Rust package is absent, but an active Python package `larkspur-tools` documents an installed `larkspur` command for the same audience. A reasonable conclusion is **REJECT** or a strong **CAUTION**, depending on the distribution plan: the executable is a practical collision even though the native registry is free. Cite the package's official command documentation, distinguish the two namespaces, and identify any unsearched channels.

## Unrelated overlap

A proposed internal library and an old unrelated art project share a display name; their packages and audiences differ. This is not automatically a rejection. **KEEP** can be reasonable with a note about the overlap, provided relevant distribution and discovery checks support it. If the library is becoming a widely marketed product, revisit how easy the name is to find and whether users could infer affiliation.

## Credible versus strained readings

A common pronunciation creates an obvious vulgar word break in the intended audience's language. Raise that early and weigh it alongside the collision evidence. Another candidate can be forced into an awkward phrase only by changing its normal pronunciation; acknowledge it if relevant without treating it as a likely reason to reject the name. The point is the audience's plausible experience, not an exhaustive list of imaginable puns.

## Missing decisive source

A registry times out and the user intends to publish there. **UNRESOLVED** is appropriate if that namespace could decide the choice. Report the failed check and what did succeed. If another verified source already shows the exact planned command is occupied by an adjacent active tool, explain that obstacle rather than letting the outage erase it.

## Respect a quick request

For an early shortlist, check the intended namespace, a focused collision search, and obvious readings. Report what was and was not checked; use a provisional recommendation. Don't turn the request into a domain, app-store, regional-language, and trademark survey unless the user asks or one of those facts is essential to the answer.

## Historical example: Catsnack

On August 28, 2026, the original Catsnack naming research found an adjacent CLI named `catnip`: its repository/package name `catnip-rs` differed from the installed command. That demonstrated why checking only an exact package name can miss a command collision. It is a historical example, not a current availability report; recheck live sources before advising on any of these names.
