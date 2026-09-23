# Lab Philosophy

## Open-Lab Principle

There is no starter solution and no mandatory tool. Each team receives a problem statement, minimum constraints, a primary metric, and a peer-voting protocol. A solution that cannot be challenged by a metric is not yet a production solution.

Teams may use public data, synthetic or simulated cases, or self-collected data, provided their experiment has sufficient ground truth or evidence to calculate the metric.

## Shared Six-Question Contract

Every team must answer:

1. What is the specific pain point, and who is harmed if it is not addressed?
2. How do you reproduce the problem? Which dataset or simulation demonstrates failure?
3. What is the baseline, and how poorly does it perform?
4. What is your solution? Why is this research, tool, algorithm, or pipeline appropriate?
5. What is the evidence? Show before/after results using a metric, not only screenshots.
6. What is the production decision: deploy, rework, or reject? State limits and next steps.

## Evaluation Rules

Evaluation cases used for the final report must not be used to tune the solution. Teams must define a development/evaluation split.

## Allowed

- Adjust a target or threshold when the use case is justified.
- Use public, synthetic, simulated, or self-collected data.
- Propose a research or open-source technique beyond the slides.
- State weaknesses in the proposed solution.

## Not Allowed

- Look up source-dataset ground truth or answers instead of running the experiment.
- Tune on the evaluation set used for final reporting.
- Change a quality threshold or decision policy after seeing ground truth.
- Substitute a demo for metric-based evaluation.
