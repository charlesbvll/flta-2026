# Exercise notebooks

Use these alongside the guide, with your downloaded Hub apps in `work/`:

Begin with [the small Flower App exercises](../docs/first-app.md) in your editor
and terminal. Then use notebooks 01–03 below. Notebook 00 is an optional
transfer of custom aggregation to a real MNIST model.

1. [Optional model aggregation](00_robust_aggregation.ipynb): implement a median and compare learning under honest, scaled-update and label-skewed conditions
2. [Digit counts](01_digit_counts.ipynb): check your two histogram functions and compare deployed IID and label-skew runs
3. [Ink statistics](02_ink_statistics.ipynb): check your moments functions, run them on the federation and record your answer
4. [Federation agent](03_federation_agent.ipynb): check your schema, arguments and cache, then query the deployed nodes through Chat

Edit the app files in your editor. Rerun a notebook's check cell after saving;
it loads the edited source again. An unfinished function should fail its check.

## Open the notebooks

Complete [setup](../docs/setup.md) and download MNIST app 0.1.0 or 0.1.1 for
notebooks 01–02. Optional notebook 00 requires 0.1.1. The agent app is released
separately before notebook 03. From the guide's root,
with its virtual environment activated:

```sh
uv pip install -r requirements-notebooks.txt
python -m ipykernel install --sys-prefix --name flta-2026 --display-name "Python (FLTA 2026)"
jupyter lab
```

Open `notebooks/01_digit_counts.ipynb` and select **Python (FLTA 2026)**. You can
also use VS Code's notebook editor with the same workspace `.venv` interpreter.
These notebooks need neither PyTorch nor a local MNIST download.

The MNIST notebooks preview remote commands by default. After logging in
and joining `@charles/flta`, set `RUN_ON_FEDERATION = True` to submit your code.
Each submission keeps its config and streamed log under `outputs/notebook-runs/`.
Keep the run ID from that stream with your observations. Interrupting a cell
stops the local stream; check the submitted run before launching it again.

For the agent, use the local synthetic checks first, then launch `flwr chat` in
a terminal as described in notebook 3. Model-free Chat still queries the deployed
nodes.

Use the blank observation cells to keep your results. Before sharing notebooks
back to this repository, clear all outputs and execution counts, then save.
The command-line exercises remain in [analytics](../docs/analytics.md) and
[the agent guide](../docs/agent.md).
