# Can we trust every model update?

This is an optional real-model extension after the
[small Flower App exercises](first-app.md). The first session's core aggregation
exercise uses two visible parameters and does not require this MNIST update.

Implement coordinate-wise median aggregation and compare it with FedAvg on the
three deployed SuperNodes. This exercise needs MNIST app **0.1.1**. Wait for
that release before starting; 0.1.0 supports the earlier exercises.
Use [notebook 00](../notebooks/00_robust_aggregation.ipynb), or the commands below.

## The question

Each selected node starts with the same global model, trains locally, and returns
a model. Its update is **local model minus the starting global model**. FedAvg
combines those updates with weights proportional to the local example counts.
Our three nodes have equal training counts, so this is their arithmetic mean.

What happens if one participant sends an update much larger than the others?
For scalar updates `[1, 2, 100]`, predict the mean and median before calculating.
Then consider legitimate disagreement: could label-skewed data produce unusual
updates even when every client is honest?

## Your code

Edit `work/paris-mnist-fl/mnist_fl/aggregation_student.py` and complete:

```python
def coordinate_median(updates):
    ...
```

Input is a finite floating NumPy array of shape `(n_clients, n_parameters)`.
Return a finite floating NumPy vector of shape `(n_parameters,)`. Take a median
separately for each parameter coordinate, across clients. Preserve the input.
For an even number of clients, use the midpoint of the two middle values.

The supplied code handles messages, parameter names, tensor shapes and dtypes,
and adding the aggregated update back to the current global model. You implement
only the statistical operation. Aggregation runs at the coordinator; training
continues to run on the deployed nodes.

From the downloaded app directory, check a small example:

```sh
python - <<'PY'
import numpy as np
from mnist_fl.aggregation_student import coordinate_median
updates = np.array([[1., -4.], [2., -3.], [100., 7.]])
before = updates.copy()
np.testing.assert_array_equal(coordinate_median(updates), [2., -3.])
np.testing.assert_array_equal(updates, before)
print("Coordinate-wise checks passed")
PY
```

## Compare two rules under one condition

Choose one condition with your group. Run FedAvg and median with the same seed,
data split, learning rate, local epochs and round count. Combine the class's
results afterward; every group does not need to run every experiment.

| Condition                      | `partition`    | `fault-partition` |
| ------------------------------ | -------------- | ----------------- |
| Honest, IID data               | `"iid"`        | `-1`              |
| IID data, one amplified update | `"iid"`        | `2`               |
| Honest, label-skewed data      | `"label-skew"` | `-1`              |

`fault-partition = -1` disables the fault. When enabled, the selected partition's
ClientApp returns `global + 20 × (local - global)`. It scales the update, not the
whole model. This is a controlled teaching fault, not a comprehensive attack.
It affects only that submitted run; it does not change the shared node setup.

In `configs/aggregation.toml`, set your condition and `aggregation = "fedavg"`.
Then run from `work/paris-mnist-fl`:

```sh
flwr run . supergrid --federation @charles/flta --run-config ../../configs/aggregation.toml --stream
```

Change only `aggregation = "median"` and run again. Keep
`aggregation-implementation = "student"`, `num-clients = 3`,
`fraction-train = 1.0` and `publish-release = false`.

Look for `FEDERATION_AGGREGATION`. Record each run ID, final accuracy and loss on
the same 900 test images. Per-round diagnostics show update norms and the distance
between the selected aggregate and the weighted mean. That distance measures
disagreement with FedAvg, not distance from an unknown correct answer.

## Explain the result

- Did your predictions match the observed results?
- Why could a median help with an extreme update?
- Which useful information could it discard under honest label skew?
- Does replacing the weighted mean preserve the same optimization objective?
- Why is a large update not sufficient evidence of malicious behaviour?
- With three clients, what remains after trimming the smallest and largest value of each coordinate?

**Checkpoint:** your code passes the small checks, and you can compare completed
FedAvg and median runs under the same condition. A median does not have to win
on test accuracy. A short neural-network experiment does not establish a general
robustness or convergence guarantee.

Next: [digit counts](analytics.md#1-how-many-of-each-digit), then ink statistics.
Optional: define a norm-clipping threshold, clip updates before averaging, and
compare how the threshold changes the result. Keep the shared analytics report
separate from these exploratory learning runs.

Background: [Yin et al., Byzantine-Robust Distributed Learning](https://proceedings.mlr.press/v80/yin18a.html).
