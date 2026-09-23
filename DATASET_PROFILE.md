# BDD100K ADAS Demo Dataset Profile

## Purpose

This document defines the raw source and the trusted-release boundary for the C6 Dataset Semantic Integrity Gate demo. The resulting dataset is an educational, VinFast-relevant front-camera ADAS perception prototype. It is not VinFast data and does not claim coverage of Vietnamese road conditions.

## Raw Source

- Dataset: BDD100K Images 100K sample.
- Local source: `BDD100k-datasample/`.
- Source documentation: `BDD100k-datasample/README.md`.
- Source license: `BDD100k-datasample/LICENSE.md`.
- Raw source must remain unchanged.
- Sample split supplied: `val` only.

## Observed Sample Inventory

| Item | Value |
| --- | ---: |
| Images | 109 |
| Per-image annotation files | 109 |
| Image dimensions | 1280 x 720 pixels |
| Total source objects | 3,378 |
| Rectangle objects | 2,291 |
| Polygon objects | 369 |
| Line objects | 718 |

The source is a Supervisely-style export: each image has a JSON file in `val/ann/` with class metadata, tags, geometry type, and coordinates.

## Trusted Release Scope

The trusted release is a canonical **COCO 2D object-detection** dataset. It retains source objects whose `geometryType` is `rectangle` and excludes lane/drivable-area geometry because they are line/polygon tasks outside the MVP detection scope.

### Approved Ontology

| COCO ID | Source class | ADAS role |
| ---: | --- | --- |
| 1 | car | Vehicle |
| 2 | truck | Large vehicle |
| 3 | bus | Large vehicle |
| 4 | person | Vulnerable road user |
| 5 | rider | Vulnerable road user |
| 6 | motor | Two-wheeler |
| 7 | bike | Two-wheeler |
| 8 | traffic light | Traffic-control signal |
| 9 | traffic sign | Traffic-control sign |

Excluded source classes:

- `lane`: line and polygon geometry.
- `drivable area`: polygon geometry.

## Release Artifacts

The builder creates `data/trusted_v1/`:

```text
data/trusted_v1/
├── annotations/instances.json  # Canonical COCO rectangles
├── images/                     # Symlinks to untouched raw image files
├── contract.json                # Approved ontology and invariants
├── manifest.json                # Image file hashes and dimensions
├── splits.json                  # Deterministic train/val/test assignment
└── RELEASE.md                   # Build provenance and commands
```

The deterministic split uses image filename order and a 70/15/15 allocation: 76 train, 16 validation, and 17 test images. It is a demo split derived from source `val` images, not an official BDD100K train/validation/test split.

## Semantic Gate Demo Boundary

The trusted release is the immutable baseline. Candidate releases must be copied from it and must remain parseable COCO-like data. The demo will intentionally introduce at least these silent corruptions:

1. Class-map or annotation category swap.
2. Bounding-box coordinate conversion/scaling error.
3. Annotation-to-existing-image linkage error.
4. YOLO normalization/round-trip geometry error.
5. Train/validation image leakage.

Each candidate must have a known expected defect label in a ground-truth evaluation manifest that the gate never reads while making its decision.

## Reproduction

After the builder is implemented, run:

```bash
python scripts/build_trusted_release.py
```

Run the release-builder test suite with:

```bash
python -m unittest discover -s tests -v
```
