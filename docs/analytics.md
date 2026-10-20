# Federated analytics

Both exercises run your code on the three deployed SuperNodes. Flower Datasets
assigns each node its own partition of the same fixed 6,000-image MNIST training
subset. The app handles loading, messages and result validation; you implement
the local summaries and their aggregation.

We compare two ways of assigning data: **IID** randomly distributes examples
across nodes, while **label-skew** gives nodes different digit distributions.
Both use the same images overall.

Work in `work/paris-mnist-fl`. The file to edit is
`mnist_fl/analytics_student.py`. Leave the transport and data-loading code as
provided for the core exercises.

## 1. How many of each digit?

**Goal:** recover the digit distribution across the whole federation, without
requesting any images at the coordinator.

Implement two functions:

| Function                    | Input                                                     | Return                                                |
| --------------------------- | --------------------------------------------------------- | ----------------------------------------------------- |
| `local_histogram(labels)`   | This node's digit labels                                  | A list of ten Python integer counts, indexed by digit |
| `merge_histograms(reports)` | A list of distinct node reports, each containing `counts` | A list of ten global counts                           |

Include a zero for a digit that does not occur locally. A message should contain
the ten counts, not labels or image identifiers.

### Try a tiny example first

From the downloaded MNIST app directory, run this after editing the functions:

```sh
python - <<'PY'
from mnist_fl.analytics_student import local_histogram, merge_histograms

a = local_histogram([0, 0, 3, 9])
b = local_histogram([3, 3, 8])
assert a == [2, 0, 0, 1, 0, 0, 0, 0, 0, 1]
assert local_histogram([]) == [0] * 10
assert merge_histograms([{"counts": a}, {"counts": b}]) == [2, 0, 0, 3, 0, 0, 0, 0, 1, 1]
print("Tiny histogram checks passed")
PY
```

### Run on the federation

```sh
flwr run . supergrid --federation @charles/flta --run-config ../../configs/histogram.toml --stream
```

The configuration selects `analytics-implementation = "student"`. Look for
`FEDERATION_ANALYTICS` in the completed output. Record the run ID, ten counts
and their total, then identify the most frequent digit.

Next, change `partition = "iid"` to `partition = "label-skew"` in
`../../configs/histogram.toml`, and submit again. Keep `num-clients = 3` and the seed
unchanged. You are changing how the app assigns data, not moving the SuperNodes.

**Checkpoint:** both runs cover exactly 6,000 images and produce the same global
histogram, despite different local distributions. Explain why local label skew
changes the node contributions but should not change their aggregate.

## 2. Which digit uses the most ink?

**Goal:** find the digit with the highest mean ink and describe how much its
images vary, again without collecting the images centrally.

For this exercise, an image's *ink* is the mean of its 784 pixel intensities,
normalized to `[0, 1]`. We want the mean and **population standard deviation of
these image-level values**, separately for each digit.

Implement the other two functions in `analytics_student.py`:

| Function                        | Input                                                        | Return                                                                        |
| ------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| `local_moments(images, labels)` | Normalized NumPy images of shape `(N, 784)` and their labels | `counts`, `sums`, `sumsq`, each a ten-element Python list                     |
| `merge_moments(reports)`        | Distinct reports with those three fields                     | The pooled `counts`, `sums`, `sumsq`, plus ten-element `mean` and `std` lists |

For a digit with no images globally, return `None` for its mean and standard
deviation. For a missing local digit, its count, sum and squared sum are zero.

Start by deciding what each node needs to send. How would you recover a variance
from those summaries? Why would averaging node means fail when a digit occurs
different numbers of times at different nodes?

<details>
<summary>Hint: sufficient statistics</summary>

For one digit, let the pooled count, sum of ink values and sum of squared ink
values be `N`, `S` and `Q`. The mean is `S/N` and the population variance is
`Q/N - (S/N)**2`. Account for small negative values caused by floating-point
rounding before taking a square root.

</details>

### Check uneven contributions

This synthetic example has one image at the first site and three at the second.
Digit 2 has different counts at the two sites, so averaging its local means
will give the wrong answer. This does not use MNIST or contact the federation.

```sh
python - <<'PY'
import numpy as np
from mnist_fl.analytics_student import local_moments, merge_moments

images = np.stack([np.full(784, value) for value in [0.2, 0.8, 0.8, 0.5]])
labels = np.array([2, 2, 2, 7])
reports = [local_moments(images[:1], labels[:1]),
           local_moments(images[1:], labels[1:])]
result = merge_moments(reports)
assert sum(result["counts"]) == 4
assert result["counts"][2] == 3
assert np.isclose(result["mean"][2], 0.6)
assert np.isclose(result["std"][2], np.sqrt(0.08))
assert np.isclose(result["std"][7], 0.0)
assert result["mean"][0] is None and result["std"][0] is None
print("Tiny moments checks passed")
PY
```

### Find the answer on the deployed nodes

```sh
flwr run . supergrid --federation @charles/flta --run-config ../../configs/moments.toml --stream
```

Repeat with `partition = "label-skew"` in `../../configs/moments.toml`. Compare counts
exactly and floating-point statistics with a small numerical tolerance.

**Checkpoint:** identify the highest-mean-ink digit, its image count, mean and
standard deviation. Keep the source run ID. The pooled result should agree
between the two partition schemes. Be ready to explain the difference between
this standard deviation and uncertainty in an estimated mean.

## From statistics to an agent

Wait for one complete global moments report to be published before the next exercise.
Your exploratory runs do not overwrite it. The approved report includes its
source run and data definition, so an answer can be traced back to a particular
computation.

During these analytics exercises, you sum **different node contributions**.
In [the agent exercise](agent.md), the nodes hold copies of that **same completed
global report**. Check their agreement and return one copy; adding those copies
would count the federation several times.
