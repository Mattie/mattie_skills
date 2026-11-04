---
name: verifier-system
description: Establish and keep a project's verification practice useful through Surface, Answer Key, and Comparison. Use for setup verifier-system, choosing how to verify agentic changes, or updating a project's verification guidance as its components evolve.
---

# Task Verifier Framework

A **Verifier** checks an agent's work against an **Answer Key**. Establishing that standard before implementation helps prevent the agent from treating its own output as proof of success. A verifier can still miss bugs or rely on a mistaken answer key, so consider its coverage and limitations.

## The 3 Parts of a Verifier

Every robust verifier consists of three components:

1. **The Surface**: The API, CLI, or UI through which a person or another system uses the component, in the contexts that matter for the task.
2. **The Answer Key**: The objective standard of success defined before the agent performs the task.
3. **The Comparison**: An automated mechanism that checks whether the actual system output matches the Answer Key, such as a structured diff, byte-for-byte comparison, or agentic judgment against a fixed rubric.

## Answer Key Ranking

Answer keys differ in reliability and the effort needed to obtain them. Use this ranking as a starting preference:

* **Tier 1: Legacy or Old Systems (Highest Reliability)**: Compare against an existing, trusted system on the same inputs, for example by replaying traffic through both versions of an API.
* **Tier 2: Snapshots & Artifacts**: Compare against trusted saved outputs, such as response fixtures, screenshots, generated files, or binary artifacts.
* **Tier 3: Independent Test Suites**: Exercise expected behavior through a suite decoupled from the implementation, such as browser tests using Playwright. Independence comes from how expectations are established and protected; a different implementation language alone does not prevent gaming.
* **Tier 4: Specifications (Lowest Reliability)**: Use requirements or a human-defined table of expected results for specific actions. Translate these into automated assertions where practical; qualitative requirements may need an agentic judge.

The ranking is a heuristic about available evidence, not a guarantee. An old system can preserve bugs, a snapshot can capture a mistake, and a precise specification can be stronger than either. Choose a key that represents the intended behavior, and combine sources when they cover different risks.

## Keeping a Verifier Useful

Establish surfaces and answer keys upfront, improve coverage when a real failure escapes, and occasionally introduce a controlled fault to see whether the verifier detects it. These are ongoing concerns, rather than separate modes or a required sequence.

Framework sources: [YouTube video](https://www.youtube.com/watch?v=JETl3kG_Ur0) and [Ray Amjad's skills](https://github.com/ray-amjad/skills). See [NOTICE.txt](NOTICE.txt) for the upstream MIT license.

## Establishing the System in a Project

When asked to `setup $verifier-system`, review what kind of project this is, its existing components and surfaces, and the tools and evidence already available. Recommend a practical default for comparing actual behavior with desired behavior through those surfaces. Keep the explanation centered on Surface, Answer Key, and Comparison; use context where it helps choose a check.

Create or update `.verifier-system/verifiers.md` as a compact map of those choices. Link to existing contracts, tests, fixtures, and commands. Make clear which approaches already exist, which are recommendations, and where evidence is missing. Record useful rationale and known limits without imposing a metadata schema or copying the project's specifications.

Start with one file. Add component records or scoped `.verifier-system/` folders only when distinct guidance warrants them, following the project's existing boundaries. Make them discoverable from the root map. Keep durable choices here and individual run output in the project's usual reports.

Recommend a brief root `AGENTS.md` hint, adapting it to existing guidance and adding it when authorized. For example:

> Consult `.verifier-system/verifiers.md` and relevant component records when changing behavior. Identify the surface, the desired behavior established by the answer key, and how actual behavior will be compared with it. Keep these choices useful as components and tools evolve. When bugs escape or checks mislead, revisit the relevant verification approach. Report what was verified and what remains unchecked.

## Applying the Framework

- **Choose what to verify.** Identify the affected surfaces, what they should do, and which existing behavior should stay the same. Where possible, establish a trustworthy answer key before making the change. Do not use the new output alone to decide what the correct result should be. Choose checks for important differences in inputs, states, and how components work together. Check both sides of limits or transitions where behavior changes. Use methods that suit the task. Let failures or differences from the answer key guide what to check next, and report important cases left unchecked.
- **Compare reality with the answer key.** Exercise the relevant surface using suitable existing tools and agreed comparison criteria. Keep the checks proportional to the task. Change expectations when intended behavior changes or the existing answer key is shown to be wrong; explain the reason rather than updating a key merely to make a check pass.
- **Carry the learning forward.** Report what ran, what matched or differed, and what remains unchecked. Update the project’s verification records when choices or gaps change, and revisit checks when bugs escape or results mislead. Report at the end of any implementation turn a clear indicator of what verifiers were created, what verifiers were used, and what remains unchecked.
