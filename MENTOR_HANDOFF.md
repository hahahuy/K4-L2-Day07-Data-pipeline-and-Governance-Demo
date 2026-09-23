# C6 Mentor Handoff: Dataset Semantic Integrity Gate

## Purpose

This document is the durable context for future agents and team members helping with Problem C6 in this repository. Treat `Problem.md` as the authoritative short challenge statement; this handoff turns it into an actionable hackathon direction without asserting unstated competition rules.

## Challenge in One Sentence

Build a dataset release gate that detects when a CVAT, COCO, YOLO, vendor merge, or versioning workflow changes the **meaning** of an object-detection dataset even though files still parse and model training can still run.

The essential question is: **did converting, merging, or versioning change the dataset semantics?**

## Hard Requirements From `Problem.md`

- Design at least five corruption types.
- Corrupted releases must remain parseable; prioritize cases where training also runs.
- Include clean releases to measure false blocks.
- Report root cause and evidence, not merely PASS/FAIL.
- Primary metric: Silent-defect Detection F1, including recall by corruption type, precision, and false-block rate on clean releases.
- Secondary metrics: root-cause localization accuracy, round-trip geometry error/IoU, and runtime per 1,000 samples.
- Stretch goal: configurable FAIL/WARN/PASS policy and machine-readable reports.

## Hackathon Evaluation Contract

The general challenge expects a fair baseline, metric-based evidence, no tuning on the final evaluation split, robustness/failure analysis, a production decision, runnable artifacts, and a five-slide presentation. See `general.md`, `lab-philosophy.md`, `pointing.md`, and `rules.md`.

## Recommended Scope

Implement a **COCO-first release gate**. Normalize all inputs to one internal representation and make COCO JSON the MVP interchange format. Support a minimal COCO <-> YOLO round-trip only if the core detector and evaluation suite are working.

Do not start with a web frontend, a learned anomaly model, or every annotation format. A reproducible CLI, controlled corruptions, strong evidence reports, and reliable metrics score better.

## Proposed Product

Example CLI:

```bash
python -m gate validate \
  --baseline data/clean_v1/annotations.json \
  --candidate data/release/annotations.json \
  --policy config/policy.yaml \
  --report reports/release_report.json
```

Expected outputs:

- Human-readable terminal summary.
- Machine-readable JSON report with status, findings, evidence, suspected root cause, and runtime.
- Nonzero exit status only for policy `FAIL`; use `WARN` for suspicious but nonblocking signals.

## Architecture

```text
Input release(s)
    -> parser and canonicalizer
    -> dataset manifests and semantic fingerprints
    -> deterministic rule checks and baseline/candidate diff checks
    -> policy engine
    -> PASS/WARN/FAIL evidence report
```

### Canonical Annotation Record

Use a small internal model per image and object:

- Image: stable ID, filename, width, height, split, optional SHA-256 and perceptual hash.
- Object: annotation ID, image ID, category ID, canonical category name, box in `[x1, y1, x2, y2]`, optional segmentation/metadata.
- Dataset contract: expected categories, approved ID-to-name mapping, format/version, provenance, and split expectations.

Convert source boxes into canonical `xyxy` exactly once. Preserve original values in evidence samples if helpful.

## Minimum Corruption Benchmark

Each corruption must produce a syntactically valid candidate release. Keep a manifest containing the known corruption label and expected localization category solely for scoring; do not expose it to the gate at validation time.

| ID | Silent corruption | Why training can run | Main detection signal | Expected localization |
| --- | --- | --- | --- | --- |
| C1 | Swap two category IDs or names in annotations | Labels remain valid integer IDs | Class-map contract and class-distribution drift | `class_mapping` |
| C2 | Interpret `xywh` boxes as `xyxy`, or rescale box coordinates | Coordinates remain numeric | Geometry invariants, area/aspect drift, round-trip IoU | `geometry_conversion` |
| C3 | Attach annotations to wrong existing images after a merge/reindex | All IDs and files can exist | Image manifest, dimension/hash mismatch, lineage comparison | `image_annotation_alignment` |
| C4 | Use the wrong image dimensions when converting normalized YOLO boxes | Resulting values are often still trainable | Containment, area drift, COCO-YOLO-COCO IoU | `normalization_conversion` |
| C5 | Introduce cross-split duplicates or move a biased subset to validation | Training and validation both run | SHA-256/perceptual-hash overlap and split/class drift | `split_integrity` |

Recommended additional cases:

- Drop a class's annotations from a subset of images.
- Duplicate annotations in a vendor merge.
- Change image metadata/provenance or category aliases without an approved contract.
- Corrupt segmentation polygons while retaining plausible bounding boxes.

## Core Checks, Ordered by Value

1. **Reference and schema integrity:** JSON parses; each annotation references a known image/category; dimensions and IDs are consistent. This is necessary but is not the main achievement.
2. **Class-map contract:** Compare ID/name mapping against a committed contract. Require an explicit migration map for intentional changes.
3. **Geometry invariants:** Require finite boxes, positive width/height, image containment tolerance, sensible area fraction, and aspect ratio limits. Report concrete violating annotations.
4. **Baseline-to-candidate semantic diff:** Compare image count, annotation count, category counts, per-class box area statistics, aspect-ratio statistics, annotations/image, image dimensions, and split distributions. Thresholds must be fixed before final evaluation.
5. **Round-trip conversion test:** COCO -> YOLO -> COCO or equivalent conversion. Match annotations by image/category and compare IoU. Report aggregate IoU plus worst examples.
6. **Image lineage manifest:** Track file name, dimensions, byte hash, optional perceptual hash, and split. Detect replaced images and unexpected image/annotation associations.
7. **Split-integrity test:** Detect exact and near duplicates across train/validation/test, then quantify class-balance changes.

## Evidence-First Report Contract

Every finding must identify the check, severity, suspected root cause, quantitative evidence, and at least a few affected samples. Do not emit bare PASS/FAIL.

Illustrative report:

```json
{
  "decision": "FAIL",
  "summary": {
    "annotations_checked": 12450,
    "failed_checks": 2,
    "runtime_ms": 310
  },
  "findings": [
    {
      "check": "class_distribution_drift",
      "severity": "FAIL",
      "suspected_root_cause": "category mapping changed or classes were relabeled",
      "evidence": {
        "category": "helmet",
        "baseline_count": 1840,
        "candidate_count": 21,
        "relative_change": -0.989
      },
      "affected_samples": ["image_0021.jpg", "image_0098.jpg"]
    }
  ]
}
```

## Policy Guidance

Use configurable policies but do not overengineer them. A simple YAML/JSON policy should contain:

- Approved class mapping and aliases.
- Maximum allowable distribution drift by signal.
- Minimum round-trip IoU.
- Maximum out-of-bounds/invalid-box rate.
- Duplicate policy per split pair.
- Decision mapping: which checks are `FAIL` versus `WARN`.

An intentional migration should be declared and auditable, not silently accepted because a threshold is loose.

## Baseline and Experiment Design

### Baseline

Use a parser-only or schema-only validator as the baseline. It should pass all five silent corruptions because they remain syntactically valid. This makes the improvement clear.

### Data

Use a small public detection dataset or a synthetic COCO dataset with known image dimensions and multiple classes. Synthetic data is acceptable and often preferable because every corruption has exact ground truth. If using public data, record its source and license.

### Split Protocol

- Development set: use to choose corruption magnitudes and policy thresholds.
- Evaluation set: held out clean and corrupted releases, never used to change thresholds.
- Clean releases: include multiple clean variants if possible, such as harmless ordering changes or approved version changes, to calculate false-block rate.

### Metrics

For each release, record expected defective/clean state, expected corruption type, gate decision, and root-cause label.

- Defect recall per corruption type = detected defective releases of that type / all defective releases of that type.
- Precision = correctly blocked defective releases / all blocked releases.
- False-block rate = clean releases blocked / all clean releases.
- Silent-defect Detection F1 should be calculated from release-level decisions unless the team explicitly justifies another unit.
- Root-cause localization accuracy = releases with correct main localization / detected defective releases, with a documented multi-finding rule.
- Round-trip geometry score = mean/median IoU and worst-case IoU.
- Runtime = total validation time / number of samples or annotations, scaled to 1,000 samples.

## Presentation Narrative

Use five slides:

1. **Pain:** A vendor merge or COCO/YOLO conversion may preserve syntax but silently change labels, geometry, or splits; training proceeds on wrong data.
2. **Baseline:** Parser/schema validation passes the corrupted releases and provides no semantic diagnosis.
3. **Solution:** Canonical model, contracts, semantic fingerprints, deterministic checks, and policy engine.
4. **Evidence:** Corruption matrix with recall by type, precision/F1, clean false-block rate, localization accuracy, runtime, and one evidence report example.
5. **Decision:** Recommend deployment as a pre-release CI gate, state known blind spots, and specify next steps such as vision-language semantic checks or learned detectors.

## Likely Review Questions and Good Answers

| Question | Answer direction |
| --- | --- |
| Is this merely schema validation? | No. Show that schema validation passes the corrupted releases, while the semantic gate blocks them with evidence. |
| How do you avoid blocking a legitimate data update? | Use a committed contract, explicit migration manifests, policy thresholds calibrated on development clean releases, and WARN for nonblocking drift. |
| What if every class distribution legitimately changes? | Distribution checks are corroborating signals, not the sole source of truth; mapping contracts and declared release changes provide context. |
| Does it scale? | Most checks are linear scans; hashes can be cached; expensive image/perceptual checks are optional or sampled. Report runtime per 1,000 samples. |
| Can it detect a perfectly plausible but completely wrong label? | Not reliably from metadata alone. State this limitation. It motivates an optional image-label model/embedding check, but that is stretch scope. |

## Non-Goals for the MVP

- Guaranteeing semantic correctness of every individual object label from annotations alone.
- Supporting every annotation format.
- Training a large vision model.
- Building a production web UI.

## Suggested Implementation Order

1. Create a tiny clean COCO release and a schema-only baseline validator.
2. Define canonical records, dataset contract, and JSON report schema.
3. Implement five deterministic corruptors and keep their ground-truth manifest outside the gate.
4. Implement class-map, geometry, distribution, lineage, and split checks.
5. Add policy-driven PASS/WARN/FAIL aggregation.
6. Run the held-out corruption benchmark and calculate all metrics.
7. Add COCO <-> YOLO round-trip only after steps 1-6 are stable.
8. Prepare the five-slide evidence narrative and a single reliable CLI demo.

## Guidance for Future Agents

- Read `Problem.md` and this handoff before suggesting implementation changes.
- Preserve the distinction between syntax validation and semantic-integrity validation.
- Do not claim detection of semantic label errors that the implemented signals cannot support.
- Keep threshold calibration separate from final evaluation to avoid cherry-picking.
- Prefer deterministic, explainable checks before learned anomaly detection.
- When changing implementation, maintain machine-readable evidence and the corruption benchmark; they are central to the primary metric.
- Ask the team what format/data is currently available before assuming COCO, YOLO, CVAT, or image access.
