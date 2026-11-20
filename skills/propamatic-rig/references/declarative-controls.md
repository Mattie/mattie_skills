# Declarative control contract

The data describes intent. Reviewed application code implements each supported operation. A schema file alone is insufficient: reject unknown fields/types and apply semantic and resource checks before using the values. This reference is a design contract, not a supplied parser or security validator.

A small hinge definition could look like:

```json
{
  "version": 1,
  "units": "m",
  "up": "+Z",
  "controls": [
    {
      "id": "lid_open",
      "default": 0,
      "kind": "hinge",
      "part": "lid",
      "pivot": [0, 0.12, 0.02],
      "axis": [1, 0, 0],
      "limits_deg": [0, 135],
      "interpolation": "linear"
    }
  ]
}
```

## Validate before constructing a scene

Accept only supported schema versions and kinds. Constrain identifiers to a short documented alphabet; resolve them through a known scene-object table. Identifiers are not filesystem paths, Python attribute paths or import names. Require unique controls and existing part references.

Require finite numeric scalars and vectors of the expected lengths, a nonzero normalized axis, ordered limits, and defaults in [0, 1]. Limit document size, nesting, control count, keyframe count, chain length, frames and solver iterations. Reject duplicate JSON keys and nonstandard NaN/Infinity rather than silently accepting ambiguous data. Choose project-appropriate numeric/resource caps before parsing or allocating attacker-controlled structures.

Add kinds only when a trusted implementation exists. For a slider, store an axis and travel interval. For a morph, store a known shape-key identifier and weight interval. For a curve, use a bounded list of numeric samples with a fixed interpolation enum. Do not invent an expression language when these operations suffice.

For dependencies, store known control IDs, a fixed operator enum and numeric thresholds or sampled mappings. For example, a latch can impose a maximum lid opening when its own normalized value passes a threshold. Define equality behavior and conflicting-dependency handling explicitly. Resolve dependencies in a validated acyclic graph; reject missing references and cycles.

Do not accept fields such as `shape_key_expr`, `pinned_when` containing executable expressions, `python`, module names, callback names, file paths or arbitrary driver text. Existing AnyMachine metadata with these fields is not safe to execute. Translate only understood semantics into the new contract; do not preserve strings through an eval compatibility layer.

## Export metadata

Keep consumer extras small and versioned: units/axes, control IDs, limits, dependencies and action names. Exclude source paths, prompts, private reference locations and credentials. Metadata must not be necessary for executing code during import. A consumer that does not understand it should still display the baked asset safely within its own parser trust boundary.
