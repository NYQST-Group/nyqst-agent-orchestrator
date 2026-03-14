# Bundle Versioning Spec

Bundles should not feel like storage plumbing. They should feel like one of the reasons to buy Intelli Studio: versioned evidence, inspectable history, meaningful diffs, and a visible relationship between source material and every downstream output. I^1 I^2

## North-Star Intent

The buyer should be able to open a bundle and immediately understand:

- what is in it
- what changed
- where it came from
- what work it powered
- what outputs and packs relate back to it

This surface should make the substrate feel serious. The user should feel that Intelli Studio can keep evidence under control even while agents and workflows are doing more ambitious work around it.

## Current-State Anchor

The repo already has a strong substrate baseline:

- `ui/src/pages/NotebookPage.tsx` already uploads files, creates manifests, advances pointers, and queries entries. I^1
- `src/intelli/services/substrate/manifest_service.py` already supports manifest creation, history, and diffs. I^2
- `src/intelli/services/substrate/pointer_service.py` and `src/intelli/db/models/substrate.py` already make pointers and pointer history real. I^3
- `ui/src/components/pointers/PointerViewer.tsx` and the workbench already expose some of that structure, though not yet as a polished buyer-facing bundle product. I^4
- `STORY-DOCS-001` through `STORY-DOCS-006` in `staging_issues/issues.json` already describe richer bundle, version, ingest, diff, and documents screens work. I^5

The wider issue normalization lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays local to the buyer-facing layer: `Bundle` as the product surface over an already real pointer-manifest-artifact substrate. The current `Notebook` naming is useful as a bridge, not as the final product answer. I^7

## Product Rules

- `Bundle` is the buyer-facing working evidence set.
- Bundle history is backed by immutable manifests and mutable pointer movement.
- The bundle surface must expose:
  - bundle detail
  - manifest history
  - diff view
  - file preview
  - related runs
  - related research packs
- File preview should make evidence usable, not merely downloadable.
- Manifest history should let the user see meaningful progression rather than raw hashes alone.
- Diff view should explain what changed and why it matters.
- Related runs and research packs should make downstream effects visible.

## Import Rules

Supported import lanes should include:

- local upload
- GitHub repository
- Git LFS-backed content where practical

Rule:

External systems are ingestion sources. Once imported, Intelli's substrate is the authoritative working record for the demo.

This matters because the buyer should see one coherent evidence surface, not a federated maze of half-owned data.

## Naming And Presentation Rules

- The UI may keep "Notebook" as an interim alias only if the surface clearly evolves toward bundle semantics.
- Buyer-facing copy should increasingly emphasize bundle history, versioning, evidence, and related outputs.
- Hashes and low-level substrate identifiers may be visible, but they must not be the only thing the user sees.
- The product should present history as readable change over time, not just backend lineage.

## Diff Rules

- Document diffs, extraction diffs, and impact diffs should all be part of the eventual story.
- Even if the first iteration is narrower, the page should clearly signal that diffs are a serious product capability.
- The user should be able to connect a changed bundle version to changed research or workflow outputs.

## Escalations Required

- The live issue corpus still spreads the document-product story across notebooks, bundles, artifact explorer, corpus organization, and structured deliverable diffing. The next agent should normalize that into one clearer bundle-versioning product lane.
- `#145` suggests corpus language that may be useful, but the north-star buyer-facing story still needs a clear bridge between current notebooks and future bundles.
- If imports from GitHub and Git LFS are important to the demo, they should probably become explicit issue language rather than staying implicit in the substrate story.

## Judgment Required

Do not ship a "bundle versioning" surface that is only a file list plus raw history metadata. The differentiator is not that versioning exists. The differentiator is that versioning, provenance, and downstream effects are understandable to a buyer. If the page reads like a developer storage console, it is not done. I^2 I^5

## Builder Accountability

The D5 builder is personally responsible for making sure:

- the bundle surface feels like a product, not a database browser
- history and diffs are readable enough that a buyer can follow the evidence story
- imports feel authoritative after landing, not like loose attachments
- related runs and research packs make downstream impact visible
- the naming bridge from current notebooks to product-grade bundles is clear

Fake completion includes:

- exposing hashes and entry counts without making meaning legible
- adding import sources without clear post-import ownership semantics
- showing diffs as raw change blobs without context
- keeping bundle-related work trapped in the dev workbench instead of turning it into a buyer-facing strength

## Issue Hooks

- `I^1` - `ui/src/pages/NotebookPage.tsx` is the current live proof that uploads, manifest creation, pointer advancement, and manifest-scoped Q&A already exist.
- `I^2` - `src/intelli/services/substrate/manifest_service.py` already supports history and diffs over immutable manifests.
- `I^3` - `src/intelli/services/substrate/pointer_service.py` and `src/intelli/db/models/substrate.py` define the current pointer, manifest, and pointer-history backbone.
- `I^4` - `ui/src/components/pointers/PointerViewer.tsx` shows that the workbench already exposes some substrate inspection surfaces that can inform the buyer-facing product.
- `I^5` - `STORY-DOCS-001` through `STORY-DOCS-006` in `staging_issues/issues.json` are direct backlog evidence for richer bundle/versioning/document screens.
- `I^6` - [docs/PLATFORM_REFERENCE_DESIGN.md](../../../docs/PLATFORM_REFERENCE_DESIGN.md) defines pointers, manifests, bundles, and immutable outputs as core substrate concepts.
- `I^7` - Live GitHub issues `#145`, `#146`, `#112`, `#82`, and `#79` show that corpus organization, locator-rich document processing, artifact provenance, structured diffing, and notebook workflow are already converging around a stronger document-product layer.
