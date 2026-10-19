# Give the agent a useful tool

The analytics app computed an answer from distributed data. Now make an agent
retrieve the approved result from the deployed SuperNodes and explain it.

Download the agent starter when Charles releases it; see the
[app download instructions](setup.md#download-the-apps).

Work in `work/paris-federation-agent`. The main file to edit is
`federation_agent/guided.py`. The supplied collector handles node discovery,
requests, replies and validation. You implement the small interface between that
collector and the agent.

The collector uses Flower's **Grid** interface to communicate with the nodes.
You can use it as provided for the main exercise.

## 3. Retrieve the approved aggregate

**Goal:** answer “Which digit has the highest mean ink?” using a checked global
report, including its count, standard deviation and source run.

Complete the three TODOs in `guided.py`:

1. Define the tool's name and allowed arguments (its schema): `get_federation_summary`, accepting an empty JSON object and no other arguments
2. Validate the requested tool name and JSON arguments before collection
3. Store the collected report under `approved_aggregate` and reuse it during the same agent run

The tool exposes one approved report. It does not accept node IDs, filters,
arbitrary queries or requests for examples. Keep node transport details out of
the result passed to the model.

### Configure your copy

In the downloaded app's `pyproject.toml`, update the existing entries under
`[tool.flwr.app.config]`. Do not add a second configuration table.

```toml
summary-source = "analytics"
release-id = "analytics-moments-v1"
cohort-id = "paris-mnist-three"
cohort-node-ids = "NODE_0,NODE_1,NODE_2"
implementation = "guided"
loop-implementation = "provided"
model-free = true
```

Replace `NODE_0,NODE_1,NODE_2` with the three decimal node IDs Charles provides,
in one comma-separated string without spaces. Use his announced release ID if
it differs. `paris-mnist-three` identifies the group of nodes that produced the
report (its cohort); it is separate from the federation name.

### Get feedback locally

After completing the TODOs, run this local check from the app directory:

```sh
python -c 'from federation_agent.cli import main; main()' --source analytics --guided --scenario complete
```

This uses synthetic replies and a scripted model. It needs no account, API key
or running nodes. It should reach a final response citing the synthetic report.
Use it to check your code before the deployed run.

### Query the deployed federation

From the same directory:

```sh
flwr chat
```

Then, inside Chat:

```text
/federation @charles/flta
/load .
Which digit has the highest mean ink? Include its count, standard deviation and the source run.
```

Start with `model-free = true`. This still sends real requests to the deployed
nodes and returns checked JSON; it does not call a language model. Once that
works, Charles will give the model settings for a natural-language answer. Set
`model-free = false` when instructed and reload with `/load .`.

The supplied model exchange handles one round of tool requests followed by an
explanation. A multi-turn agent loop is an optional extension.

Reload after every source or app-configuration change. `/load` takes the app
directory, while the configuration lives in `pyproject.toml`.

**Checkpoint:** your modified agent retrieves the approved moments report from
all three real nodes. Keep its source run and identify the statistic's
population. Its answer should agree with the approved analytics output. A local
synthetic run alone does not complete this checkpoint.

## 4. Make the tool reliable

**Goal:** reject unsupported requests and avoid repeating the same collection.

Test the argument checks and caching you added to `guided.py`:

| Call or condition | Expected behaviour |
| --- | --- |
| `get_federation_summary` with the JSON string `{}` | Collect and return the approved aggregate |
| An unknown tool name | Return an error without collection |
| Extra arguments, such as `{"node_id": "123"}` | Return an error without collection |
| Malformed JSON or a JSON array | Return an error without collection |
| A repeated valid call in the same agent run | Reuse the first result |
| Missing or conflicting evidence | Return a generic error, with no partial report |
| A repeated call after collection failed | Reuse the failure, without another collection |

The cache belongs to one agent run. A new Chat prompt can start a new collection.

### Check that invalid calls never reach the Grid

Use an assertion or a small spy around the Grid interface. For example:

```sh
python - <<'PY'
from federation_agent.guided import SummaryTool
from federation_agent.replay import FIXTURE_CONFIG

class NoNetwork:
    def call(self, request):
        raise AssertionError("Invalid arguments reached collection")

tool = SummaryTool(NoNetwork(), dict(FIXTURE_CONFIG))
for name, arguments in [
    ("unknown_tool", "{}"),
    ("get_federation_summary", '{"node_id": "123"}'),
    ("get_federation_summary", "[1, 2]"),
    ("get_federation_summary", "{broken"),
]:
    result = tool.dispatch(name, arguments)
    assert result.get("error") and "approved_aggregate" not in result
print("Invalid calls rejected")
PY
```

### Check repeated calls and bad evidence

```sh
python -c 'from federation_agent.cli import main; main()' --source analytics --guided --scenario complete --repeat 2
python -c 'from federation_agent.cli import main; main()' --source analytics --guided --scenario missing --repeat 2
python -c 'from federation_agent.cli import main; main()' --source analytics --guided --scenario conflicting
python -c 'from federation_agent.cli import main; main()' --source analytics --guided --scenario wrong-source
```

Inspect the final response and `grid_calls`. One successful collection
uses discovery, send and receive: three Grid calls. Repeating the tool call
within the same run should not double that work. Missing replies after send
and receive should also be cached as a failure. Rejected arguments should make
zero Grid calls.

Keep errors generic: a missing report should not expose local paths or raw node
replies to the model. After your local checks, reload the app and confirm that
your successful deployed query still works.

**Checkpoint:** demonstrate an invalid call that performs no collection, a
repeated success, a repeated failure, and a working retrieval from the deployed
federation. Explain why three agreeing copies are evidence for one global result,
rather than three contributions to add together.
