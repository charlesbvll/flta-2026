"""Load edited student files and run the workshop commands from a notebook."""

import importlib
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path


def app_directory(root, name):
    path = Path(root) / "work" / name
    if not (path / "pyproject.toml").is_file():
        raise FileNotFoundError(
            f"Download {name} into {Path(root) / 'work'} first; see docs/setup.md"
        )
    return path


def _load_student(root, app, name):
    directory = app_directory(root, app)
    source = directory.joinpath(*name.split(".")).with_suffix(".py")
    if not source.is_file():
        raise FileNotFoundError(f"Expected student file: {source}")
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
    parent = importlib.import_module(name.rpartition(".")[0])
    if Path(parent.__file__).resolve().parent != source.parent.resolve():
        raise RuntimeError("Another app copy is loaded; restart this notebook's kernel")
    module = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location(name, source)
    )
    # Read source again on every check, including edits made within one second.
    exec(
        compile(source.read_text(encoding="utf-8"), str(source), "exec"),
        module.__dict__,
    )
    return module


def analytics_student(root):
    return _load_student(root, "paris-mnist-fl", "mnist_fl.analytics_student")


def guided_agent(root):
    return _load_student(root, "paris-federation-agent", "federation_agent.guided")


def _flwr():
    path = Path(sys.executable).with_name("flwr.exe" if os.name == "nt" else "flwr")
    if not path.is_file():
        raise RuntimeError("Choose the workshop Python kernel; it must include Flower")
    return str(path)


def _command_text(command):
    return subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)


def run_analytics(root, mission, partition, *, execute=False, federation="@charles/flta"):
    """Preview or submit student analytics; preserve its config and streamed log."""
    root = Path(root)
    app = app_directory(root, "paris-mnist-fl")
    if mission not in {"histogram", "moments"} or partition not in {"iid", "label-skew"}:
        raise ValueError("Choose histogram or moments, and iid or label-skew")
    cfg = tomllib.loads((root / "configs" / f"{mission}.toml").read_text())
    expected = {
        "task": "analytics",
        "analytics-mission": mission,
        "analytics-implementation": "student",
        "num-clients": 3,
        "save-output": False,
        "publish-release": False,
    }
    if any(
        type(cfg.get(key)) is not type(value) or cfg[key] != value
        for key, value in expected.items()
    ):
        raise ValueError("Use the three-node, non-publishing student exercise config")
    cfg["partition"] = partition
    folder = root / "outputs" / "notebook-runs"
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{mission}-{partition}-{uuid.uuid4().hex[:8]}"
    config = folder / f"{stem}.toml"
    config.write_text(
        "".join(f"{key} = {json.dumps(value)}\n" for key, value in cfg.items()),
        encoding="utf-8",
    )
    command = [
        _flwr(), "run", ".", "supergrid", "--federation", federation,
        "--run-config", str(config), "--stream",
    ]
    print(f"App directory: {app}")
    print(_command_text(command))
    if not execute:
        print("Preview only. After login and membership, set RUN_ON_FEDERATION = True.")
        return None
    log = folder / f"{stem}.log"
    print(f"Saving the stream to {log}")
    with log.open("w", encoding="utf-8") as saved:
        process = subprocess.Popen(
            command,
            cwd=app,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        try:
            for line in process.stdout:
                print(line, end="", flush=True)
                saved.write(line)
                saved.flush()
            returncode = process.wait()
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            process.stdout.close()
    if returncode:
        raise RuntimeError(f"Flower exited with status {returncode}; inspect {log}")
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", log.read_text(encoding="utf-8"))
    for line in reversed(text.splitlines()):
        if "FEDERATION_ANALYTICS " in line:
            payload = line.split("FEDERATION_ANALYTICS ", 1)[1]
            summary, _ = json.JSONDecoder().raw_decode(payload)
            if summary.get("mission") != mission or summary.get("total_count") != 6000:
                raise ValueError(f"Unexpected aggregate; inspect {log}")
            return {"summary": summary, "log": log, "config": config}
    raise RuntimeError(
        f"No completed analytics result in {log}; check the run before resubmitting"
    )


def replay_agent(root, *, scenario="complete", repeat=1):
    """Run the downloaded app's synthetic harness against its guided student code."""
    app = app_directory(root, "paris-federation-agent")
    command = [
        sys.executable, "-c", "from federation_agent.cli import main; main()",
        "--source", "analytics", "--guided", "--scenario", scenario,
        "--repeat", str(repeat),
    ]
    result = subprocess.run(
        command, cwd=app, text=True, capture_output=True, timeout=60, check=False,
    )
    print(result.stdout, end="")
    if result.returncode:
        print(result.stderr, end="")
        raise RuntimeError("The guided student code did not pass; fix the error above")
    return json.loads(result.stdout)
