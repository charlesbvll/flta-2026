# FedProx with Flower

Material for the [FLTA Summer School in Paris](https://school.flta-conference.org/index.php),
20–21 October 2026

Follow a federated learning experiment from setup to results: understand the FedProx
objective, inspect its implementation, compare it with FedAvg in simulation, then run
the same app on a federation of laptops.

## Get started

You need a terminal, an editor and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Use Linux or Apple Silicon macOS, or WSL on Windows. No GPU is needed.

**Follow the [FedProx walkthrough](docs/fedprox.md).** It includes:

1. Downloading and preparing the complete app
1. Running FedAvg and FedProx in simulation
1. Reading the proximal loss and strategy code
1. Comparing learning curves, local updates and unequal work budgets
1. Connecting a laptop as a SuperNode and running the same app again

Work individually, in pairs or in a small group. For laptop federation runs, create
a [Flower account](https://flower.ai) and submit your username for an invitation.
Wait for the federation name, participant count and partition ID before connecting.

The complete app is distributed through [Flower Hub](https://flower.ai/apps/charles/fedprox/)
as `@charles/fedprox`. Download it once the release is available. Its source and run
configurations come together; this repository contains the guide and
[background references](docs/resources.md).
