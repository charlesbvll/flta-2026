# Change a Flower App

We will start with a tiny model whose entire state is two numbers. This makes
every client reply and aggregation result visible. The app runs on the same
three deployed SuperNodes that we will use for MNIST later.

Complete [account and environment setup](setup.md) first. Wait for the opening
app to be available on Hub, then download it from your guide workspace:

```sh
mkdir -p work
cd work
flwr new @charles/paris-first-app==0.1.0
cd paris-first-app
```

If you already downloaded this app, keep that directory and your edits.
`flwr new` downloads editable source. Each `flwr run .` submits your saved local
version, so different groups can submit different code to the same federation.
There is no need to restart or change the shared nodes.

## Read the app, then run it

| File                      | What to find                                            |
| ------------------------- | ------------------------------------------------------- |
| `pyproject.toml`          | ServerApp/ClientApp entry points and run configuration  |
| `first_app/client_app.py` | The train-message handler, local computation and reply  |
| `first_app/server_app.py` | Initial parameters, round orchestration and aggregation |

The initial model is `[0, 0]`. At partition `p`, local training takes one gradient
step on `||w − target||² / 2`, with target `[p + 1, −(p + 1)]` and learning rate
0.5. Each site initially has aggregation weight 1. Predict the three returned
models and the aggregate before running:

```sh
flwr run . supergrid --federation @charles/flta --stream
```

Find `FIRST_APP_ROUND` and `FIRST_APP_RESULT`. The first-round aggregate should
be `[1, -1]`. Inspect each contribution rather than just the final line.
The parameters have shape `(2,)` at each client. Stacking three replies gives
shape `(3, 2)`; aggregation returns a single `(2,)` model again.

The starter uses synthetic local objectives, without a dataset download.
There is no held-out evaluation or accuracy metric in this small app.

## Exercise 1: change what a client returns

Edit `local_train` in `first_app/client_app.py`. Replace the local gradient step
with these fixed returned model parameters, selected by `partition_id`:

| Partition | Returned model parameters |
| --------- | ------------------------- |
| 0         | `[1, -4]`                 |
| 1         | `[2, -3]`                 |
| 2         | `[100, 7]`                |

Keep the function signature and return one finite NumPy vector of shape `(2,)`.
Leave the message wrapper and weights unchanged. This deliberately replaces
optimization with a controlled computation so you can predict the network result.
These are returned models, not deltas to add to the incoming model.

From this app directory, check your function locally:

```sh
python - <<'PY'
import numpy as np
from first_app.client_app import local_train
expected = [[1., -4.], [2., -3.], [100., 7.]]
for partition, values in enumerate(expected):
    result = local_train(np.zeros(2), partition, 0.5)
    assert isinstance(result, np.ndarray) and result.shape == (2,)
    np.testing.assert_array_equal(result, values)
print("Client values checked")
PY
flwr run . supergrid --federation @charles/flta --stream
```

**Checkpoint:** all three expected vectors appear in `FIRST_APP_ROUND`, and the
aggregate is approximately `[34.333333, 0]`. Keep the run ID.

Explain why the first coordinate moves so much. Which line controls the local
computation, and which code transports its result? What would happen if every
client returned the same vector because you forgot to use `partition_id`?

## Exercise 2: change the aggregation rule

Keep your client changes. Edit `aggregate_vectors` in
`first_app/server_app.py`. Replace the weighted mean with a **coordinate-wise
median**: independently take the middle value across clients for every parameter.
Keep the input unchanged and return a finite NumPy vector of shape `(2,)`.
For an even number of synthetic inputs, use the midpoint of the two middle values.

The supplied strategy calls your function with vectors of shape
`(number_of_clients, number_of_parameters)` and one weight per client. Your
median is unweighted; it deliberately does not use those weights.

```sh
python - <<'PY'
import numpy as np
from first_app.server_app import aggregate_vectors
vectors = np.array([[1., 9.], [2., 0.], [100., 3.]])
original = vectors.copy()
result = aggregate_vectors(vectors, np.ones(3))
assert result.shape == (2,)
np.testing.assert_array_equal(result, [2., 3.])
np.testing.assert_array_equal(vectors, original)
np.testing.assert_array_equal(
    aggregate_vectors(np.array([[0., 2.], [4., 8.]]), np.ones(2)),
    [2., 5.],
)
print("Aggregation checked")
PY
flwr run . supergrid --federation @charles/flta --stream
```

**Checkpoint:** the same three clients still return `[1, -4]`, `[2, -3]` and
`[100, 7]`, but the aggregate is now `[2, -3]`. Compare with your previous run.
The tiny local check also produces a vector that no client submitted: different
coordinates can come from different clients.

Discuss what median protects against here and what it ignores. An unusually
large update could come from a fault or from useful information in different
local data. This controlled example demonstrates influence on aggregation;
it does not establish a robustness or convergence guarantee for neural networks.

## If you finish early

- Set `unequal-weights = true` in the existing app config, then compare your median with the starter's weighted mean using weights 1, 2 and 3
- Run two rounds with `--run-config 'num-server-rounds=2'` and explain why fixed returned models stop changing the result, whereas the original gradient step keeps moving it
- Return a fixed delta added to the incoming model instead of a fixed model, then predict the two-round result
- Implement clipping before averaging and compare the effect of different thresholds
- Transfer the same aggregation idea to a real model with the optional [MNIST aggregation exercise](aggregation.md)

A weight changes how much a client influences a weighted average. In this tiny
app the weights are synthetic numbers, not measured dataset sizes. In ordinary
FedAvg they usually represent local training-example counts. Changing the
aggregation rule can change the optimization objective.

## Continue with connected data

Next, use the [MNIST analytics app](analytics.md) to count actual distributed
images and compute ink statistics. That exercise sends small summaries instead
of model parameters. Later, an agent will retrieve one approved global report.
Keep each experiment's source code and run ID so the result is reproducible.
