# Getting started

You need Git, a terminal, an editor and
[uv](https://docs.astral.sh/uv/getting-started/installation/). The commands below
use a macOS or Linux shell. On Windows, use WSL for the same commands, or use the
PowerShell activation command noted below.

## Create your workspace

```sh
git clone https://github.com/charlesbvll/flta-2026.git
cd flta-2026
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv pip install "flwr==1.40.0" "numpy==2.4.3" "openai==2.28.0"
flwr --version
```

In PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of `source`.
Use the workshop's Flower version even if you already have another environment.
The OpenAI package is used by the agent's local harness; installing it does not
require an API key. You do not need a personal model API key for the exercises.

This environment is enough to edit the apps, run the small local checks and
submit work to the deployed federation. Downloading MNIST, installing PyTorch
and running a SuperNode on your laptop are optional later steps.

## Join the federation

Create or sign in to your account through [Flower](https://flower.ai), then give
Charles your **Flower username** so he can arrange membership and agent access.
After he has sent your invitation:

```sh
flwr login supergrid
flwr federation invite accept @charles/flta supergrid
flwr federation list supergrid --federation @charles/flta
```

You should be able to see the workshop federation and its three SuperNodes.
If the invitation or agent access is missing, check with Charles before changing
your environment.

## Download the apps

Once Charles confirms that the Hub releases are available:

```sh
mkdir -p work
cd work
flwr new @charles/paris-mnist-fl==0.1.0
flwr new @charles/paris-federation-agent==0.1.0
cd ..
```

`flwr new` downloads editable app source. Your workspace should now contain:

```text
flta-2026/
  configs/                         run configurations from this guide
  docs/                            exercise instructions
  notebooks/                       interactive exercise worksheets
  work/
    paris-mnist-fl/                 learning and analytics app
    paris-federation-agent/         agent app
```

The `work/` directory is ignored by Git. Keep your exercise changes there or in
your own repository. If you already downloaded an app, keep your edits rather
than overwriting its directory with another download.

To work through the exercises in Jupyter, follow the
[notebook setup](../notebooks/README.md#open-the-notebooks). This adds Jupyter to
the same environment; it does not require local training dependencies.

## Run along with the training demonstration

From the guide's root directory:

```sh
cd work/paris-mnist-fl
flwr run . supergrid --federation @charles/flta --run-config ../../configs/train.toml --stream
```

The `.` matters: it submits your local app, including source changes. Running an
app by its Hub identifier instead would use the published release.

This run trains for three rounds on the deployed nodes. Look for the selected
clients, the local training results and the aggregate evaluation. Keep the run
ID if you want to compare results later. Concurrent runs may queue; give a
submitted run time to finish before submitting it again.

For the coding exercises, use [the analytics guide](analytics.md). Your ordinary
runs have `save-output = false` and `publish-release = false`; they do not replace
the shared report used by the agent.

## If something gets stuck

| Symptom | Check |
| --- | --- |
| `flwr` is missing, or shows a different version | Activate this workspace's `.venv` in the current terminal |
| Hub download fails | Check the app name, version and publication status above |
| Permission denied on the federation | Check that you logged in with the invited Flower account and accepted the invitation |
| A run fails at a `TODO` | This is expected until the selected student function is implemented |
| The output does not reflect an edit | Save the file and submit `flwr run .` from the downloaded app directory |
| Agent output does not reflect an edit | Save the file, then reload the agent with `/load .` |
| A node is unavailable | Keep the error and ask Charles; do not change the shared node processes |

When asking for help, share the command, run ID and relevant error. Keep access
tokens and private keys out of screenshots and issues.
