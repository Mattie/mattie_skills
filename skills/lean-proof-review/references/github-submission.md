# GitHub submission and distribution

Use this reference only when GitHub PRs, Actions, or releases are the submission or distribution route. Apply the general [artifact, privacy, and receipt guidance](artifact-validation.md); reuse repository tooling and existing evidence formats rather than prescribing a new verification framework.

## Pull request CI

Run relevant integrity and preservation checks, publication/privacy checks, and verification-tool regression tests on PRs. Verify workflow triggers, path filters, and build matrices against the project's package and advertised-target inventory. Cover every package and target in scope rather than copying a hard-coded example count.

Validate receipts selected to support current claims. Use relevant input changes and applicable receipts to select affected proof work. Historical receipts for previous identities may remain as history without satisfying the current check. Distinguish a fresh proof run, validated reuse, a skipped build, and a pending run. If expensive builds require manual dispatch, surface that pending state before claiming completion; a routine CI pass does not establish that separately dispatched work ran.

Ensure the checkout contains the pinned history needed for provenance checks. Configure necessary read-only authentication for upstream queries without exposing credentials or broadening permissions unnecessarily. A network or authentication failure leaves the provenance check incomplete; it does not establish a false theorem.

## Proof runs and retained evidence

Propagate command failures through logging pipelines. Retain useful logs on success and failure, configure hidden output directories deliberately when collecting artifacts, and fail required evidence collection when files are missing. Successful compilation with incomplete evidence retention is not a completed auditable verification step.

Report publication checks, proof compilation, axiom checks, independent replay, specification comparison, and log retention separately. A green job for one claim cannot establish the others. Bind execution receipts to checked inputs and the producing run. For validated reuse, reference the original execution receipt and provenance instead of claiming a fresh run. An untrusted, hand-authored pass marker is not evidence of independent execution.

Budget time, memory, disk, and concurrency for the actual proof jobs, and disclose cache provenance. Select work by the affected inputs and validation routes; a documentation-only PR need not cause a full proof rebuild. Preserve durable release evidence when Actions artifact expiry would otherwise break the promised reproduction path.

## Release and submission checks

Before authorized publication, verify the prepared distribution's inventory, privacy, licenses and notices, transport identities, and uncompressed proof identities. Label download URLs as planned until they are live. Keep local verification, prepared distribution, and reviewer-accessible evidence distinct.

After authorized publication, retrieve the documented files with the access available to the intended reviewer, verify their identities, and record the retrieval check. Recheck access at submission milestones, including artifact expiry and access-policy changes. This is separate from replaying an unchanged proof; a failed download leaves a retrieval gap without discarding valid historical proof evidence.

Use stable source references and accurate CI links tied to the checked revision or demonstrably unchanged relevant proof inputs. Update stale claims that a run is pending or successful. If evidence is unavailable or required checks remain incomplete, report the exact gap and the supported local result.

Verification and preparation do not authorize posting, publishing, merging, or approving a later GitHub gate. Follow the human's authorization for those actions and report any pending approval without approving it on their behalf.
