# Federated learning and analytics with Flower

Hands-on material for the [FLTA Summer School in Paris](https://school.flta-conference.org/index.php), 20–21 October 2026, with Charles Beauville

How much can we learn from data held by several organisations, without bringing
their examples into one place? We will start with a small federated learning run,
write our own federated statistics, then build an agent that can use the result.

**Start with [setup](docs/setup.md).** You can work individually, in pairs or in
a small group. Bring a laptop and an editor; the main exercises run on deployed
SuperNodes, so you do not need a GPU.

## The sessions

| Session | What we will do | Hands-on goal |
| --- | --- | --- |
| 1 | Daniel's remote introduction, a walkthrough of Flower's architecture and a first run | Recover the federation's digit distribution |
| 2 | Compute statistics over distributed data | Find which digit uses the most ink and measure its variability |
| 3 | Connect an agent to the federation | Retrieve an approved aggregate, then handle invalid requests and missing evidence |

The architecture and first training run are guided demonstrations. You are
welcome to run along. The coding exercises are in
[federated analytics](docs/analytics.md) and [the agent](docs/agent.md).
If you finish early, pick an [extension](docs/extensions.md), including connecting
your own SuperNode.

## Workshop links

| Resource | Where to go |
| --- | --- |
| Setup and account access | [Getting started](docs/setup.md) |
| Exercise 1: digit counts | [Global histogram](docs/analytics.md#1-how-many-of-each-digit) |
| Exercise 2: ink statistics | [The ink question](docs/analytics.md#2-which-digit-uses-the-most-ink) |
| Exercises 3 and 4: agent tools | [Build the agent](docs/agent.md) |
| Optional challenges | [Go further](docs/extensions.md) |
| Documentation and background | [References](docs/resources.md) |

The shared federation is `@charles/flta`. The optional node challenge uses
`@charles/flta-playground`, after checking with Charles.

The apps will be distributed through [Flower Hub](https://flower.ai/apps) under
`charles`, separately from this guide:

- [MNIST learning and analytics](https://flower.ai/apps/charles/paris-mnist-fl/): `@charles/paris-mnist-fl==0.1.0`
- [Federation agent](https://flower.ai/apps/charles/paris-federation-agent/): `@charles/paris-federation-agent==0.1.0`

App publication is still pending. Charles will confirm when downloads are ready
and announce any version change here. You can complete the environment and
account setup first.

## What data moves?

The exercises use public MNIST images, split between three deployed SuperNodes
with Flower Datasets. Analytics runs use a fixed subset of 6,000 training images.
The learning demonstration evaluates on a separate set of 900 test images.

For analytics, each node computes a small summary of its own partition. The
coordinator combines those summaries without requesting images. Later, the agent
retrieves an approved global report held by the nodes. The coordinator can see
individual node summaries; this workshop does not add secure aggregation or
differential privacy.

This repository contains the guide and run configurations. Download and edit the
apps from Hub when the exercises begin.
