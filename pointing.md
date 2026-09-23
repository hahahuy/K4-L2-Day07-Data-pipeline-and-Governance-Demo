# Peer Voting and Scoring

Every group evaluates every other group in its class using one 100-point rubric, then casts one Best Solution vote. Teams cannot evaluate themselves.

## Rubric

| Criterion | Evaluator evidence | Points |
| --- | --- | ---: |
| Pain point and problem framing | A concrete real problem with clear constraints and assumptions | 10 |
| Metric validity | The primary metric measures the pain point and the test protocol is valid | 15 |
| Technical solution | A logical, runnable prototype or research method that fits the problem | 20 |
| Experiment and evidence | Fair baseline, clear before/after result, no cherry-picking | 25 |
| Robustness and failure analysis | Edge cases, limitations, slice tests, or stress tests | 10 |
| Production feasibility | Scale, cost, integration, and risks considered | 10 |
| Presentation and Q&A | Clear explanation and evidence-based answers | 10 |
| Total |  | 100 |

## Scoring Procedure

1. Each evaluator submits a 0-100 rubric score for every other team.
2. A team's Peer Rubric Score is the median of scores it receives.
3. Each evaluator casts one Best Solution vote for another team.
4. The team with the most Best Solution votes wins the cluster. A tie is broken by Peer Rubric Score.
5. The winner receives five bonus points, capped at 100.

## Innovation Bonus

| Bonus | Requirement |
| --- | --- |
| +5 | Apply a research or open-source technique beyond the slides and explain its mechanism correctly |
| +10 | Improve a technique or add a meaningful evaluation or robustness experiment |
| +15 | Present a credible production or research direction: automation, configurable policy, scalability, or a new reusable insight |

Bonus cannot compensate for an invalid primary metric or experiment.

## Minimum Submission

- Runnable source code, notebook, or demo.
- README with reproduction instructions.
- Dataset/source description and license or source link.
- Baseline and primary-metric result.
- Evaluation split/protocol.
- Failure or limitation note.
- Five-slide showcase PDF or PPTX.

Cloud deployment, a polished frontend, and a large trained model are optional. Prioritize experimental quality and evidence.
