# What data is connected to the federation?

Starting from the NumPy quickstart, find the digit distribution across the
currently connected SuperNodes. Return summaries rather than individual labels.

```sh
uvx flwr new @flwrlabs/quickstart-numpy
cd quickstart-numpy
```

If you have already downloaded this app, keep your directory and edits.
The untouched starter uses dummy arrays and has no dataset. For this exercise,
Each SuperNode has a prepared, fixed local file containing its MNIST labels.
The files stay fixed between runs; your app should read them rather than download
or repartition data.

## The local data contract

Each node's `context.node_config["workshop-dir"]` names its existing local workshop
directory. Under it, `local-data/labels.npy` contains a one-dimensional NumPy array
of integer digit labels in the range 0–9. Read it with NumPy and
`allow_pickle=False`. This path belongs to the remote node, not your laptop.

You do not need `partition-id` in this app. That setting was used once during
data preparation. The connected SuperNode's real identity comes
from Flower's message metadata.

## Your task

1. Replace the dummy local computation with a ten-bin label histogram
1. Return ten integer counts and the number of local examples
1. Discover the connected nodes, send a query to each and combine their summaries
1. Display each node's distribution under its real node ID and the pooled result

Only the ClientApp should open the label file. The ServerApp must work using
replies alone. Keep all ten bins even when a class is absent locally.
No additional dataset or ML library is needed in the app.

Run your saved changes on the federation:

```sh
uvx flwr run . supergrid --federation @charles/flta --stream
```

## Hints

- `Grid.get_node_ids()` discovers the connected nodes
- A custom `query.distribution` message can be handled with `@app.query("distribution")`
- `MetricRecord` can carry a list of counts and a sample count
- `reply.metadata.src_node_id` identifies the responding node
- Think about what to do if a queried node fails or does not reply

## Checkpoint

Report the connected node IDs, each node's histogram, the pooled histogram and
its total. Explain why counts should be summed and what population your result
covers. Does disconnecting a node change anyone else's local data?

Each of the three prepared sites holds 2,000 labels from a fixed 6,000-example
MNIST training subset. A successful query of all three should cover 6,000 examples.
If fewer sites are connected at discovery time, the result covers only those
sites. A failed reply must not silently count as an empty dataset.

The data is public teaching data and the nodes share a server. Separate files
model separate data owners; they do not provide filesystem isolation. The
coordinator sees node-level histograms. This exercise does not add secure
aggregation or differential privacy.

For further statistics exercises, continue with [federated analytics](analytics.md).
