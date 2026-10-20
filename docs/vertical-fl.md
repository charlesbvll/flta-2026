# Vertical FL: different features for the same examples

This optional walkthrough uses the [official Flower VFL example](https://flower.ai/docs/examples/vertical-fl.html)
to train a split neural network on Titanic passenger data. Start after the
[FedProx walkthrough](fedprox.md), or follow the code without running it.

## What changes from FedProx?

|                 | FedProx tutorial                        | This VFL example                                            |
| --------------- | --------------------------------------- | ----------------------------------------------------------- |
| Data ownership  | Different examples, same feature schema | Different features for the same aligned examples            |
| Client model    | A complete classifier                   | A feature encoder                                           |
| Labels          | Available at each client                | Held by the ServerApp                                       |
| Client sends    | Trained model parameters                | Per-example embeddings                                      |
| Server combines | Model parameters by weighted averaging  | Embeddings by concatenation, then a learned prediction head |
| Server sends    | Global model and training settings      | Gradients with respect to each embedding block              |

The three feature parties hold these columns:

- Partition 0: age and sex
- Partition 1: fare, siblings/spouses aboard and name
- Partition 2: parents/children aboard and passenger class

The ServerApp holds the survival labels. Every party must use the same passenger
order: row 0 of every feature block must describe the passenger whose label is at
row 0. The example assumes this alignment rather than implementing entity matching.

## What is an embedding here?

It is the output of a client's encoder forward pass. For each passenger, each
encoder produces 64 learned values. These are intermediate activations, not model
weights or the final prediction. They need not be smaller than the original features.

For `N` passengers, each client sends an `N × 64` matrix. The server concatenates
the three matrices along their feature dimension, producing `N × 192`, then applies
its prediction head to produce one survival probability per passenger.

## Follow one training round

1. Request embeddings from all three feature parties with `query.generate_embeddings`
1. Concatenate the replies in feature-partition order and compute predictions and loss
1. Backpropagate through the server head to obtain its parameter gradients and the gradient of each embedding block
1. Update the head and send each embedding gradient to its originating party with `train.apply_gradients`
1. Recompute each local forward pass with the saved encoder, apply the received gradient and update the encoder
1. Wait for every update acknowledgement before starting the next round

Sending arrays across a message does not send a PyTorch computation graph. The
local recomputation rebuilds that graph so `embedding.backward(received_gradient)`
can apply the chain rule to the encoder's parameters. Encoder weights and Adam
optimizer state persist between messages in `context.state`.

One round is one full-batch update of all model parts. There is no FedAvg-style model
averaging. This is a split-learning implementation of VFL; other VFL methods can use
different models and communication protocols.

## Run a short simulation

Use a separate directory from the FedProx app. You need Git and the same supported
host and uv setup. Download only the example directory from the Flower repository:

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/flwrlabs/flower.git flower-vfl
cd flower-vfl
git sparse-checkout set examples/vertical-fl
cd examples/vertical-fl
uv sync --python 3.12
```

If you already have the example, open its directory instead. Start with 30 rounds:

```sh
uv run flwr run . local \
    --federation-config 'num-supernodes=3 client-resources-num-cpus=1 client-resources-num-gpus=0.0 init-args-num-cpus=2 init-args-num-gpus=0' \
    --run-config 'num-server-rounds=30' --stream
```

The configuration creates three virtual feature parties using two CPU workers.
Look for embedding requests followed by gradient messages each round. Loss and accuracy
appear at round 25 and the final round. The default full run is 250 rounds; replace
`30` with `250` to run it.

These are **training metrics**, measured before that round's updates, with no held-out
test set. Look for learning, but do not interpret high training accuracy as evidence
of generalization. Initialization is not fixed, so exact results vary.

## Read the code and discuss the limits

- In `vertical_fl/task.py`, find the column partitioner, row ordering and encoder/head models
- In `vertical_fl/client_app.py`, follow both handlers and the saved model/optimizer state
- In `vertical_fl/server_app.py`, follow embedding collection, concatenation, loss, gradient routing and acknowledgements

What would break if one party shuffled its rows independently? Why does this model
need every feature party, rather than sampling arbitrary clients? What additional
evaluation would you add before reporting a research result?

The example uses Flower's Message API for a custom protocol. It waits for both
exchanges each round and does not demonstrate asynchronous training. Public data is
downloaded before selecting columns, so the partitioning illustrates ownership rather
than enforcing access control. Embeddings and gradients can reveal information;
this example adds neither secure computation nor differential privacy.

[Official documentation](https://flower.ai/docs/examples/vertical-fl.html) ·
[Example source](https://github.com/flwrlabs/flower/tree/main/examples/vertical-fl)
