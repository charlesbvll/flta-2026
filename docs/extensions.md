# Go further

Pick a challenge once your current exercise works. There is no need to finish
every extension; choose something you can implement and demonstrate.

## After your first Flower App

- Compare equal and unequal weights in the small app
- Change returned models into additive updates and predict a second round
- Transfer the aggregation rule to a real model with the optional [MNIST exercise](aggregation.md)

## After MNIST model aggregation

- Compare your rule under another condition using the same seed and round count
- Define and implement norm clipping before averaging; explain how the clipping threshold changes influence
- Explain why coordinate-wise median can combine coordinates from different clients
- Consider unequal local sample counts: what changes when replacing weighted averaging with an unweighted median?

## After the histogram

- Add a check that the pooled count equals the expected population, including when a local digit is absent
- Return global digit proportions and compare the most common and least common labels
- Compare IID and label-skew runs: keep the global answer fixed and explain the different local summaries

## After the ink statistics

- Test an uneven per-digit split that would break a mean-of-means implementation
- Try a numerically more stable merge for variance and compare it with the sum-of-squares approach on synthetic data
- Design a federated ink histogram with a fixed set of bins, then estimate a quantile from it

For a new deployed statistic, extend the local summary and server aggregation
together. Confirm the message format before running it on shared nodes. Keep replies aggregate;
do not add raw images, labels or example identifiers. New statistics belong in
exploratory runs, not in the shared approved report.

## After the agent

- Add local cases for duplicate replies, wrong request correlation and collection deadlines
- Explain and test the collector's fixed-cohort checks, then implement a collector of your own for the analytics report format
- Copy `federation_agent/student_loop_template.py` to `federation_agent/student_loop.py`, complete the loop and select `loop-implementation = "student"`
- Use the local check command's `--student-loop`, `--scenario tool-limit` and `--scenario turn-limit` options to test execution limits

Keep the guided implementation working while you develop an extension. If you
write your own collector, make it read the analytics report used in this course.
The provided model exchange handles one round of tool requests. The optional
student loop should support repeated model/tool turns, with a shared tool-call
budget and matching call IDs. Test it with repeated calls and both limit cases.

## Connect your own SuperNode

**Goal:** operate a participant that is both online and a member of the assigned
federation. Wait for access to `@charles/flta-playground` before connecting. Keep the
main three-node federation unchanged during the core exercises.

This needs more setup than submitting an app: a supported host, the app's local
dependencies and dataset cache, a node key, account membership and a running
SuperNode process. Use a workshop machine intended for running the exercise apps.

1. Request playground membership and wait for your partition ID and the intended participant count
1. Prepare Python 3.12 and the downloaded MNIST app's dependencies, including Flower Datasets and PyTorch, using its `pyproject.toml`
1. Accept the invitation, register your node's public key and add the node from your own account
1. Start the node with your assigned partition configuration
1. Verify that it is online and listed in the playground federation

Follow the [SuperNode connection guide](https://flower.ai/docs/framework/how-to-connect-supernodes-to-supergrid.html)
for host preparation. On supported Linux or Apple Silicon macOS, the app's
dependencies can be prepared from `work/paris-mnist-fl` with
`uv sync --python 3.12`; use `uv run` for the node commands in that environment.
On Windows, use WSL. On Intel macOS, use a supported Linux host instead
of installing the node dependencies locally.

The commands below assume those dependencies are ready and you are in the
downloaded MNIST app directory. Use a new key filename if one already exists.

```sh
uv run flwr login supergrid
uv run flwr federation invite accept @charles/flta-playground supergrid

mkdir -p "$HOME/flta-node"
ssh-keygen -t ecdsa -b 384 -N "" -f "$HOME/flta-node/node-key"
uv run flwr supernode register "$HOME/flta-node/node-key.pub" supergrid --name "FLTA my-node"
```

Replace `NODE_ID` below with the returned number to add your node to the federation.

```sh
uv run flwr federation add-supernode NODE_ID @charles/flta-playground supergrid
```

Replace `PARTITION_ID` with your assigned integer. Keep the private key on
your machine. In this terminal:

```sh
uv run flower-supernode \
    --superlink api.flower.ai:443 \
    --auth-supernode-private-key "$HOME/flta-node/node-key" \
    --host 127.0.0.1 --port 9094 \
    --node-config "partition-id=PARTITION_ID workshop-dir=\"$HOME/flta-node/reports\""
```

Keep the process running. From another terminal in the same app directory:

```sh
uv run flwr supernode list supergrid --verbose
uv run flwr federation list supergrid --federation @charles/flta-playground
```

**Checkpoint:** your node is online in the first listing and present in the
federation listing. Registration alone does not complete the challenge. The
first app run will download and cache the public dataset locally.

For an agreed four-node experiment, use four distinct partition IDs
`0–3`, `num-clients = 4` and `publish-release = false`. This is a new experiment;
your node does not become part of an older three-node report. Use the same
dataset definition and app version on all participating nodes.

Wait until the shared experiment is finished, then stop your process with Ctrl+C
and remove your node from the playground federation:

```sh
uv run flwr federation remove-supernode NODE_ID @charles/flta-playground supergrid
```

Removing federation membership leaves your account's node registration intact.
