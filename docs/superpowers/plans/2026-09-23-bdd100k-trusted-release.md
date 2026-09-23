# BDD100K Trusted Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible COCO trusted release, image manifest, and deterministic split from the local BDD100K Supervisely sample.

**Architecture:** A single standard-library Python builder reads raw per-image annotations, preserves only approved rectangle classes, and writes canonical COCO data plus metadata under `data/trusted_v1/`. Tests use tiny temporary source fixtures so they verify conversion behavior without modifying or depending on the full dataset.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, SHA-256, filesystem symlinks.

---

### Task 1: Document the data boundary

**Files:**
- Create: `DATASET_PROFILE.md`

- [ ] **Step 1: Record source facts and scope**

Document the local source location, sample inventory, approved rectangle ontology, excluded lane/drivable-area geometry, release artifacts, deterministic split policy, and the five planned corruptions.

- [ ] **Step 2: Verify the profile is source-grounded**

Run:

```bash
python -c "from pathlib import Path; text=Path('DATASET_PROFILE.md').read_text(); assert '109' in text; assert '2,291' in text; assert 'BDD100k-datasample/' in text"
```

Expected: command exits with code 0.

### Task 2: Test expected COCO conversion

**Files:**
- Create: `tests/test_build_trusted_release.py`
- Create: `scripts/__init__.py`

- [ ] **Step 1: Write a failing conversion test**

Create a temporary raw layout with one `1280 x 720` placeholder image and one Supervisely JSON annotation containing one `car` rectangle, one `lane` line, and one `drivable area` polygon. Assert that `build_release()` creates one COCO image, one COCO annotation with `[10, 20, 20, 40]`, and only the nine approved categories.

- [ ] **Step 2: Run the focused test and confirm failure**

Run:

```bash
python -m unittest tests.test_build_trusted_release.TrustedReleaseBuilderTest.test_build_release_converts_only_approved_rectangles -v
```

Expected: `ModuleNotFoundError` or `ImportError` because `scripts.build_trusted_release` does not exist.

- [ ] **Step 3: Implement the minimal builder**

Create `scripts/build_trusted_release.py` with `build_release(source_root, output_root)`. It must:

- read raw images from `source_root/val/img` and annotations from `source_root/val/ann`;
- map the nine approved source class names to IDs 1-9;
- convert two exterior points `[x1, y1]`, `[x2, y2]` to COCO `[min_x, min_y, width, height]`;
- skip all non-rectangle and unapproved source objects;
- write `annotations/instances.json`.

- [ ] **Step 4: Run the focused test and confirm success**

Run:

```bash
python -m unittest tests.test_build_trusted_release.TrustedReleaseBuilderTest.test_build_release_converts_only_approved_rectangles -v
```

Expected: PASS.

### Task 3: Test and implement release metadata

**Files:**
- Modify: `tests/test_build_trusted_release.py`
- Modify: `scripts/build_trusted_release.py`

- [ ] **Step 1: Write failing metadata tests**

Assert that `build_release()` writes:

- `contract.json` with `format` equal to `COCO` and a nine-class approved mapping;
- `manifest.json` with a SHA-256 and real width/height for each image;
- `splits.json` whose image IDs are disjoint and whose union equals all COCO image IDs;
- an `images/` symlink for each source image.

- [ ] **Step 2: Run the focused metadata test and confirm failure**

Run:

```bash
python -m unittest tests.test_build_trusted_release.TrustedReleaseBuilderTest.test_build_release_writes_contract_manifest_splits_and_links -v
```

Expected: FAIL because metadata artifacts do not exist yet.

- [ ] **Step 3: Implement metadata artifacts**

Extend `build_release()` to:

- create one relative symlink per raw image under `output_root/images/`;
- compute streaming SHA-256 hashes;
- use image dimensions from raw annotation `size`, validating that they are positive;
- split sorted image IDs into 70%, 15%, and remainder partitions using integer floors, producing 76/16/17 for 109 images;
- write `contract.json`, `manifest.json`, `splits.json`, and `RELEASE.md`.

- [ ] **Step 4: Run all builder tests**

Run:

```bash
python -m unittest tests.test_build_trusted_release -v
```

Expected: PASS.

### Task 4: Provide a reproducible command and build the real release

**Files:**
- Modify: `scripts/build_trusted_release.py`
- Create: `data/trusted_v1/annotations/instances.json`
- Create: `data/trusted_v1/contract.json`
- Create: `data/trusted_v1/manifest.json`
- Create: `data/trusted_v1/splits.json`
- Create: `data/trusted_v1/RELEASE.md`
- Create: `data/trusted_v1/images/` symlinks

- [ ] **Step 1: Add a command-line entry point**

Add `argparse` defaults:

```python
source_root = Path("BDD100k-datasample")
output_root = Path("data/trusted_v1")
```

The command must refuse an output path outside the repository only if explicitly supplied and must overwrite only generated output files inside the selected output root.

- [ ] **Step 2: Build the actual trusted release**

Run:

```bash
python scripts/build_trusted_release.py
```

Expected: reports 109 images, 2,291 rectangle annotations, 9 categories, and split counts 76/16/17.

- [ ] **Step 3: Verify actual release invariants**

Run:

```bash
python -c "import json; from pathlib import Path; root=Path('data/trusted_v1'); coco=json.loads((root/'annotations/instances.json').read_text()); splits=json.loads((root/'splits.json').read_text()); assert len(coco['images']) == 109; assert len(coco['annotations']) == 2291; assert len(coco['categories']) == 9; assert [len(splits[name]) for name in ('train','val','test')] == [76,16,17]"
```

Expected: command exits with code 0.

### Task 5: Final verification

**Files:**
- Modify: `DATASET_PROFILE.md`

- [ ] **Step 1: Run the full tests**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: PASS.

- [ ] **Step 2: Confirm source integrity**

Run:

```bash
git diff --no-index -- /dev/null BDD100k-datasample/README.md >/dev/null; test -f BDD100k-datasample/val/ann/b5753b26-33163d42.jpg.json
```

Expected: the annotation file test passes; do not modify any raw-source file.

- [ ] **Step 3: Update reproduction documentation**

Ensure `DATASET_PROFILE.md` provides the exact builder and test commands and explicitly states that the 70/15/15 split is demo-only.
