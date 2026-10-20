# Federated learning and analytics with Flower

Hands-on material for the [FLTA Summer School in Paris](https://school.flta-conference.org/index.php), 20–21 October 2026

How much can we learn from data held by several organisations, without bringing
their examples into one place? We start with a small federated learning run,
change a Flower App and write our own federated statistics. On Wednesday we
investigate local training with FedProx and run a federation on our laptops.

**Start with [setup](docs/setup.md).** You can work individually, in pairs or in
a small group. Bring a laptop and an editor; the main exercises run on deployed
SuperNodes, so you do not need a GPU.

**Wednesday:** follow [FedProx: from simulation to laptops](docs/fedprox.md).
We will take a researcher's workflow from question and experimental setup through
code, controlled runs and interpretation, then run the same app on our laptops.
Wait for the app release and laptop federation details before connecting a node.

## The sessions

| Session | What we will do                                   | Hands-on goal                                                           |
| ------- | ------------------------------------------------- | ----------------------------------------------------------------------- |
| 1       | Create an app from Hub and change its computation | Change what clients return, then implement custom model aggregation     |
| 2       | Compute statistics over distributed data          | Find which digit uses the most ink and measure its variability          |
| 3       | FedProx in simulation and on our laptops          | Follow a complete baseline, compare experiments and operate a SuperNode |

Start with [your first Flower App](docs/first-app.md): run it on the deployed
federation, change the local computation and change aggregation. Continue with
[federated analytics](docs/analytics.md) or its
[notebooks](notebooks/README.md). The [agent material](docs/agent.md) remains an
optional extension.
If you finish early, pick an [extension](docs/extensions.md), including connecting
your own SuperNode.

## Workshop links

| Resource                                 | Where to go                                                           |
| ---------------------------------------- | --------------------------------------------------------------------- |
| Setup and account access                 | [Getting started](docs/setup.md)                                      |
| Interactive exercise worksheets          | [Open the notebooks](notebooks/README.md)                             |
| First-session coding exercises           | [Change a Flower App](docs/first-app.md)                              |
| Live NumPy distribution challenge        | [Query connected data](docs/numpy-distribution.md)                    |
| Wednesday: FedProx and laptop SuperNodes | [From simulation to laptops](docs/fedprox.md)                         |
| Optional real-model aggregation          | [Can we trust every model update?](docs/aggregation.md)               |
| Exercise 1: digit counts                 | [Global histogram](docs/analytics.md#1-how-many-of-each-digit)        |
| Exercise 2: ink statistics               | [The ink question](docs/analytics.md#2-which-digit-uses-the-most-ink) |
| Optional agent tools                     | [Build the agent](docs/agent.md)                                      |
| Optional challenges                      | [Go further](docs/extensions.md)                                      |
| Documentation and background             | [References](docs/resources.md)                                       |

The shared federation is `@charles/flta`. The optional node challenge uses
`@charles/flta-playground`; wait for membership and partition details before joining.

The apps are distributed through [Flower Hub](https://flower.ai/apps) under
`charles`, separately from this guide:

- [Opening app](https://flower.ai/apps/charles/paris-first-app/): `@charles/paris-first-app==0.1.0` — download once the release is available
- [MNIST learning and analytics](https://flower.ai/apps/charles/paris-mnist-fl/): `@charles/paris-mnist-fl==0.1.0` for analytics; optional real-model aggregation needs `0.1.1`
- [FedProx](https://flower.ai/apps/charles/fedprox/): `@charles/fedprox==0.1.0` — complete Wednesday app; download once the release is available
- [Federation agent](https://flower.ai/apps/charles/paris-federation-agent/): `@charles/paris-federation-agent==0.1.0` — released before the agent exercise

Start with the opening app, then use MNIST notebooks 01–02 for analytics.
MNIST version `0.1.0` is already available for training and analytics. The optional
real-model aggregation notebook 00 needs `0.1.1`; wait for that
release before starting it. The agent starter follows before notebook 03.

## What data moves?

The opening app uses synthetic two-parameter objectives so every value is visible.
The later exercises use MNIST, a public dataset of handwritten digit images, split
between three deployed SuperNodes with Flower Datasets. Analytics runs use a fixed
subset of 6,000 training images.
The learning demonstration evaluates on a separate set of 900 test images.
The Wednesday FedProx app uses 6,000 training and 900 test images, with training
partitions assigned to the agreed number of participating laptops

For analytics, each node computes a small summary of its own partition. The
coordinator combines those summaries without requesting images. In the optional exercise, the agent
retrieves a published global report for the agent exercise
(the "approved report"). The coordinator can see
individual node summaries; this workshop does not add secure aggregation or
differential privacy.

This repository contains the guide, exercise notebooks and run configurations.
Download and edit the apps from Hub when the exercises begin.
