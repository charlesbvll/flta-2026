# FedProx: how far should local training move?

Train a small MNIST classifier with Flower's Message API, first in simulation and then
on a federation of laptops. The model is logistic regression: 784 pixel values go
directly to 10 class logits. No GPU or torchvision is needed. The app is complete: follow the code and run
controlled experiments without implementing the baseline. Follow the same sequence you
would use for a research experiment: define the question, fix the setup, check a
working control, change one factor, and inspect the evidence.

One complete app, `@charles/fedprox`, contains both comparisons and runs in simulation
or on connected SuperNodes. Use `conf/fedavg.toml` for mu=0 and `conf/fedprox.toml`
for mu=1. Both configurations use the same source code.

This is a classroom adaptation of [FedProx](https://arxiv.org/abs/1812.06127), not a
reproduction of its published experiments. We use 10 participants and a fixed
6,000-image training subset, with a separate 900-image test subset. The original
baseline uses many more participants, a different partitioning scheme and longer
training. Here, Flower Datasets provides IID or Dirichlet label-skew partitions of the
same public training images.

## Get the app

Once the app release is available, download it:

```sh
uvx flwr new @charles/fedprox
cd fedprox
```

If you have the complete app as a ZIP, extract it and open its directory instead.
The commands below submit your local copy.

## Prepare

From this app's directory, on supported Linux or Apple Silicon macOS:

```sh
uv sync --python 3.12
uv run python -m fedprox_app.prepare
```

Use the same prepared environment for local simulation and for running a SuperNode. On
Windows, use WSL for these shell commands. PyTorch 2.10 does not provide Intel macOS
wheels; use a supported machine for local execution.

## Start with FedAvg

Before running, write down what you are comparing. The first question is whether adding
the proximal penalty changes local movement and early learning under label skew. Keep
the data, model, learning rate, local epochs, rounds and participation fixed.

Run the control:

```sh
uv run flwr run . local \
    --federation-config conf/simulation.toml \
    --run-config conf/fedavg.toml --stream
```

The simulation configuration creates 10 virtual SuperNodes with two CPU workers.
`num-partitions=10` in the app must match that population. Each node gets its own
`partition-id` automatically. All 10 participate in every round by default.

Follow `FEDPROX_EVALUATION` for held-out loss and accuracy; round 0 is the untrained
model. Each node prints one `FEDPROX_CLIENT` line with its round, partition ID, dataset
size and local epochs. The preparation command prints its label counts. Server training
metrics show mean cross-entropy and update norm, weighted by local example counts.
Update norm is the Euclidean distance from that round's received model after local
training.

## Follow the proximal term

Open `fedprox_app/task.py` and read `proximal_penalty`. The function receives the
current model, a tuple of fixed parameter copies from the start of this round, and the
coefficient mu. The local objective is:

```text
local cross-entropy + (mu / 2) * sum over all parameters of (parameter - anchor)^2
```

The sum includes every weight and bias coordinate. PyTorch tracks gradients through
the current parameters. The anchor stays fixed for the whole local training call
and is replaced when the next global model arrives.

Predict the effect of the proximal term on the first optimizer step, then on later
steps. Run the complete FedProx configuration:

```sh
uv run flwr run . local \
    --federation-config conf/simulation.toml \
    --run-config conf/fedprox.toml --stream
```

Use either one run-config TOML file or inline key-value overrides; Flower does not
combine a config file with additional inline overrides.

The server uses a small `FedProx` class in `fedprox_app/server_app.py`. It inherits
from Flower's `FedAvg` and adds `proximal-mu` to each training message. Sampling and
sample-weighted aggregation are inherited unchanged. The client uses the received
coefficient in its local loss. Setting mu to zero recovers ordinary local SGD and FedAvg
aggregation.

## Inspect the result before drawing a conclusion

A submitted job is not proof that training succeeded. Check for ten results and zero
failures in each round, then find the final `FEDPROX_RESULT` line. It includes the
held-out curve and aggregated training metrics. A flat accuracy curve with failed
ClientApps is an execution problem, not an optimizer comparison.

Compare the complete curves, not just the last number. Does the penalty reduce local
movement? Does that also improve held-out accuracy within five rounds? Those are
separate questions. The reported update norm is the sample-weighted mean of each
client's distance from the received global model, not the norm of the aggregate update.

For a research project, keep the source, configuration, dependency lock, versions, run
IDs and logs with your results. You do not need to archive them during this tutorial.
These short single-seed runs illustrate behavior. For a research
comparison, use validation data for selecting hyperparameters, an untouched test set
for final evaluation, and repeated seeds to measure variation.

## Compare one change at a time

Keep the seed, population, partitioning, learning rate, work budget and round count
fixed when changing mu. Try mu values 0, 0.1, 1 and 10. Compare the whole accuracy/loss
curve and update norms. A larger penalty can reduce drift while slowing learning;
FedProx is not guaranteed to beat FedAvg in every experiment.

To investigate data heterogeneity, repeat with `partition="iid"`, keeping the same 6,000
training examples. Dirichlet alpha controls how label-skewed the partitions are; this
setup does not promise exactly two labels per participant.

For unequal local work, pass the settings together as inline overrides:

```sh
uv run flwr run . local \
    --federation-config conf/simulation.toml \
    --run-config 'proximal-mu=1.0 variable-local-epochs=true' --stream
```

A deterministic rotating third of the participants then trains for fewer epochs. This
models unequal work budgets; it does not simulate network delays or asynchronous
aggregation. Every received update is still weighted by the number of local training
examples, not by its number of epochs.

If you want to explore further:

- Plot update norm and held-out loss as mu changes
- Predict what a very large mu does, then check it
- Compare IID and label skew at the same local epoch budget
- Increase local epochs and investigate when regularization helps or hurts
- Reduce `fraction-train` and discuss participation versus data heterogeneity

## A comparison with longer, unequal local work

The default is already non-IID: `partition="label-skew"` and Dirichlet
`partition-alpha=0.3`. The standard FedAvg/FedProx config files change only mu.

For a more demanding local-training comparison, run:

```sh
uv run flwr run . local --federation-config conf/simulation.toml --run-config conf/unequal-fedavg.toml --stream
uv run flwr run . local --federation-config conf/simulation.toml --run-config conf/unequal-fedprox.toml --stream
```

Both configurations use ten clients, ten rounds, learning rate 0.5 and a rotating work
budget: most clients train for 20 epochs, approximately a third for 6. All participate,
and aggregation still weights by local example counts. Only mu differs: 0 versus 0.1.

A real local Flower simulation at seed 42 produced:

| Method          | Final test accuracy | Final test loss | First-round mean local update norm |
| --------------- | ------------------- | --------------- | ---------------------------------- |
| FedAvg          | 85.2%               | 0.549           | 7.09                               |
| FedProx, mu=0.1 | 86.7%               | 0.483           | 2.89                               |

This illustrates a useful regime for the proximal term: more local work can make each
update more specific to its own distribution. Constraining that movement can improve
the combined model. The setting was selected after exploratory comparisons; the gain
is modest and is not guaranteed for other settings. FedAvg learns faster early in this
run, so compare the full curves as well as the final values. For research, tune both methods
using validation data and compare across seeds with an untouched final test set.

## Run the same app on laptops

Wait for the federation name, participant count and your unique partition ID.
Only one laptop per working group needs to run a SuperNode. The examples below use
`@charles/flta-laptops`; replace it if a different federation is announced.

Wait for your invitation, then accept it and register your node from the app directory:

```sh
uvx flwr login supergrid
uvx flwr federation invite accept @charles/flta-laptops supergrid
mkdir -p "$HOME/flta-fedprox"
ssh-keygen -t ecdsa -b 384 -N "" -f "$HOME/flta-fedprox/node-key"
uvx flwr supernode register "$HOME/flta-fedprox/node-key.pub" supergrid --name "FLTA my-laptop"
```

Register a key only once. If it is already registered, reuse its existing node ID.
Keep the private key on your machine. Set `NODE_ID` to the registration result:

```sh
NODE_ID="replace-with-the-returned-node-id"
uvx flwr federation add-supernode "$NODE_ID" @charles/flta-laptops supergrid
```

The values `N=10` and `PARTITION_ID=0` below are examples. Replace them with the
assigned values before running. IDs are unique integers from 0 to N-1; N is the number
of participating laptops.

```sh
N=10
PARTITION_ID=0
uv run python -m fedprox_app.prepare --partition-id "$PARTITION_ID" --num-partitions "$N"
uv run flower-supernode \
    --superlink api.flower.ai:443 \
    --auth-supernode-private-key "$HOME/flta-fedprox/node-key" \
    --host 127.0.0.1 --port 9094 \
    --node-config "partition-id=$PARTITION_ID"
```

Keep that terminal open. `uv run` uses the environment containing the app's PyTorch and
dataset dependencies. A CLI-only `uvx flwr` environment is sufficient for submitting
work, but is not the prepared ClientApp environment.

From another terminal in the same app directory, inspect membership:

```sh
uvx flwr supernode list supergrid --verbose
uvx flwr federation list supergrid --federation @charles/flta-laptops
```

Wait for confirmation that all nodes are ready and that a shared run can start.
Submit each shared run once. In this second terminal, set `N` to the same participant
count used above (10 is an example), then run:

```sh
N=10
uvx flwr run . supergrid --federation @charles/flta-laptops \
    --run-config "proximal-mu=1.0 num-partitions=$N" --stream
```

Do not pass the simulation configuration to this deployed run. The app waits for N
online nodes before training. Keep the data, seed, mu and local work settings consistent
when comparing with simulation. Laptop partition IDs must also match. Changing N changes
the partitioning and therefore the experiment.

These are real connected SuperNodes computing on assigned public MNIST partitions. The
exercise does not read participants' personal files or turn MNIST into private data. The
ServerApp evaluates on the separate public test subset. It receives model updates and
training metrics, not training images; this app does not add secure aggregation or
differential privacy.

The loop is synchronous: it waits for replies from the selected clients each round.
Unequal local epochs and client sampling do not make it asynchronous.

## Read the code

| File            | Role                                                              |
| --------------- | ----------------------------------------------------------------- |
| `server_app.py` | Small FedProx strategy, initial model and held-out evaluation     |
| `client_app.py` | Receive arrays/configuration, load one partition, train and reply |
| `task.py`       | Model, proximal penalty, local optimizer and test evaluation      |
| `data.py`       | Fixed subsets and Flower Datasets partitioners                    |

[Original paper](https://arxiv.org/abs/1812.06127) ·
[Flower FedAvg strategy](https://flower.ai/docs/framework/ref-api/flwr.serverapp.strategy.FedAvg.html)
· [Flower baseline](https://flower.ai/docs/baselines/fedprox.html)
