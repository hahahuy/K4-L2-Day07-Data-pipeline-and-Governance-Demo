# C6 Pipeline Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a dependency-free, browser-ready visual demo of the C6 ADAS dataset semantic-integrity gate pipeline.

**Architecture:** One HTML file contains semantic structure, inline CSS, inline SVG connectors, and native JavaScript state transitions. A Python `unittest` reads the file to verify the presentation contract without a browser dependency.

**Tech Stack:** HTML5, CSS, inline SVG, browser DOM APIs, Python standard-library `unittest`.

---

### Task 1: Specify the browser-demo contract in a failing test

**Files:**
- Create: `tests/test_pipeline_animation.py`

- [ ] **Step 1: Write a failing structural test**

Create a test that reads `demo/pipeline-animation.html` and asserts all of the following literal contract elements exist:

```python
required_text = [
    "Trusted ADAS Release",
    "Vendor conversion + merge",
    "JSON parses",
    "Training loader accepts",
    "Class-map contract",
    "Geometry drift",
    "Image linkage",
    "Round-trip IoU",
    "Split leakage",
    "FAIL",
    "Play",
    "Pause",
    "Restart",
    "Step",
    "prefers-reduced-motion",
]
```

Also parse the file with `html.parser.HTMLParser` and fail when an external `http://` or `https://` `src` attribute appears.

- [ ] **Step 2: Run the test and confirm failure**

Run:

```bash
python -m unittest tests.test_pipeline_animation -v
```

Expected: FAIL because `demo/pipeline-animation.html` does not exist.

### Task 2: Implement the static pipeline visual

**Files:**
- Create: `demo/pipeline-animation.html`

- [ ] **Step 1: Create the visual shell**

Add a responsive, dark operations-console page with these sections:

- Header identifying the C6 Dataset Semantic Integrity Gate and the VinFast-relevant ADAS context.
- `aria-live="polite"` current-stage status text.
- Five left-to-right pipeline cards: trusted release, vendor conversion/merge, candidate release, semantic gate, and evidence report.
- Inline SVG connector paths between cards.
- Five initially-pending check rows inside the semantic-gate card.
- An initially-hidden/low-emphasis FAIL evidence report with only illustrative scenario data.
- A presenter-note disclaimer that this is a simulated target scenario until backed by the actual gate output.

Use no external assets, icons, fonts, images, CSS, JavaScript, or libraries.

- [ ] **Step 2: Run the test and confirm partial contract success/failure**

Run:

```bash
python -m unittest tests.test_pipeline_animation -v
```

Expected: any remaining failure identifies missing controls, reduced-motion support, or interaction text.

### Task 3: Implement animation state and controls

**Files:**
- Modify: `demo/pipeline-animation.html`

- [ ] **Step 1: Add native state transitions**

Implement JavaScript with five stages:

```javascript
const stages = ["trusted", "conversion", "candidate", "gate", "report"];
```

`showStage(index)` must apply an `is-active` class to completed/current cards, progressively reveal the five check rows at the gate stage, and reveal the report at the final stage. It must update the live status string.

- [ ] **Step 2: Add accessible controls**

Implement four native buttons:

- Play advances every 1.4 seconds and stops at the report.
- Pause clears the active timer.
- Restart resets to stage zero and hides check/report completion states.
- Step clears the timer and advances exactly one stage.

Use `setInterval` only while playing; keep the active timer in one variable and clear it before starting another timer.

- [ ] **Step 3: Add reduced-motion behavior**

Use a `window.matchMedia("(prefers-reduced-motion: reduce)")` query. When it matches, initialize to the final stage and do not start automatic transitions. CSS must also disable transitions under the media query.

- [ ] **Step 4: Run the structural test**

Run:

```bash
python -m unittest tests.test_pipeline_animation -v
```

Expected: PASS.

### Task 4: Verify local serving and presentation readiness

**Files:**
- Modify: `demo/pipeline-animation.html`

- [ ] **Step 1: Parse and check dependencies**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: all trusted-release and animation tests pass.

- [ ] **Step 2: Verify the file is served locally**

Run:

```bash
python -m http.server 8765 --directory demo >/tmp/c6-animation-server.log 2>&1 & server_pid=$!; sleep 1; curl --fail --silent http://127.0.0.1:8765/pipeline-animation.html >/dev/null; kill $server_pid
```

Expected: command exits with code 0.

- [ ] **Step 3: Add usage note at the bottom of the page**

Include the exact local presentation command:

```bash
python -m http.server 8765 --directory demo
```

and the URL `http://localhost:8765/pipeline-animation.html`.

- [ ] **Step 4: Commit**

```bash
git add demo/pipeline-animation.html tests/test_pipeline_animation.py docs/superpowers/plans/2026-09-23-c6-pipeline-animation.md docs/superpowers/specs/2026-09-23-c6-pipeline-animation-design.md
```
