# C6 Pipeline Animation Design

## Goal

Create a browser-ready, offline animation that explains why a semantic dataset release gate is needed in a VinFast-relevant ADAS perception workflow.

## Scope

The artifact is a single `demo/pipeline-animation.html` file with inline CSS, SVG, and JavaScript. It will require no package installation, CDN, local server, dataset access, or external assets.

The page communicates this fixed narrative:

1. A trusted ADAS release contains 109 frames, 2,291 detection boxes, and nine approved classes.
2. A vendor conversion/merge produces a candidate release.
3. The candidate is syntactically valid and a training loader can accept it.
4. The semantic integrity gate scans five signals.
5. The gate returns a FAIL decision with concrete example evidence.

## Visual Design

Use a dark operations-console visual language with cool slate surfaces, a restrained red alert state, bright green only for syntax/training acceptance, and a small warm highlight for the candidate packet. The pipeline is left-to-right on desktop and remains readable on narrow displays through horizontal scroll or stacked cards.

The central visual is a sequence of cards connected by animated SVG paths:

```text
Trusted release -> Vendor conversion / merge -> Candidate -> Semantic gate -> Evidence report
```

The gate displays five visible checks: class-map contract, geometry drift, image linkage, round-trip IoU, and split leakage. The final report must state that it is a simulated target demo scenario until the actual gate produces a real report.

## Interaction

Provide Play, Pause, Restart, and Step controls. The animation begins paused to let the presenter choose the pace. Play executes the full timeline; Step advances one stage at a time; Restart resets all stages to their initial state.

Respect `prefers-reduced-motion`: show the final state without timed motion while retaining controls and content.

## Implementation

Use native DOM class toggles plus CSS transitions/keyframes. Use inline SVG for connectors and scan lines. Do not use GSAP, Motion, Manim, canvas, external images, or CDN dependencies.

The file must use semantic buttons, live status text for the current stage, and sufficient color contrast. The animation represents the planned pipeline, not a claim that the gate checks already run against a release.

## Verification

1. Confirm the HTML is structurally valid enough to parse with Python's `html.parser`.
2. Confirm it contains all controls and five named checks.
3. Serve it locally with `python -m http.server` and fetch it with `curl` to verify a `200` response.
4. Open it in a browser before presenting to validate layout and animation manually.
