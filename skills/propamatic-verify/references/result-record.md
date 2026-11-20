# Verification result record

Use the project's existing format where available. This is a compact set of evidence to preserve, not a requirement to create a large report for every tweak.

Record the candidate's path, hash and build/run identifier; the Blender/exporter and target-runtime versions; the reference/specification revision; and the verification command/environment. Use sanitized artifact-relative paths when the record will be shared.

Each check needs a status (`pass`, `fail`, `unverified`, or `not_applicable`), expected behavior or tolerance, observed measurement, and evidence when useful. Failure and unverified status are never equivalent to pass. Mark not-applicable only with a reason, such as no animation on a static prop.

For motion, record controls and combinations sampled, frame/time intervals, sample count, worst observed clearance/slip/pose error and excluded intentional contacts. Sampling is evidence about those samples; it is not proof for unsampled continuous states. A formal guarantee would need a different method and stated assumptions.

For visual comparison, keep the actual reference and output views, camera/scale correspondence and specific discrepancies. Source-versus-export similarity alone cannot show that either matches the intended design.

For export checks, identify the re-imported hash and compare evaluated source/export states at known parameter values. Record target-engine checks separately. A file that re-imports in Blender may still behave differently in the consuming engine.

A failed build cannot produce a current passing export record. Check that expected outputs belong to this run; stale files and success-shaped console output are not evidence. End with whether the artifact is ready for the intended use and any limitations that affect that judgment.
