---
name: offload
description: Port a Python function in the user's code to run on Readie with the @remote decorator, choosing packages, memory and GPU settings and removing pickling hazards.
argument-hint: "<function name or file:line>"
disable-model-invocation: true
---

# Offload a function to Readie

Make the function `$ARGUMENTS` run on Readie with `@remote`. Read the `readie` skill's
`reference/sdk.md` first.

## 1. Check the local setup

Run these and report problems before editing code:

```bash
python --version
python -c "import readie; print(readie.__version__)"
```

- Python must be 3.12.x. Otherwise suggest `uv venv --python 3.12` (the client raises
  `IncompatiblePythonError` on anything else).
- If `readie` is missing, suggest adding it with the project's tool (`uv add readie`,
  `poetry add readie`, or `pip install readie`). Do not install without asking.
- `READIE_AUTH_TOKEN` is read from the environment if the service requires one. Never
  write a token into the code.

## 2. Inspect the function

Find the function and everything it touches. Flag each of these:

- **Unpicklable inputs or captured objects**: open files, sockets, DB clients, locks,
  threads, loggers with handlers. Move their creation inside the function, and pass
  paths, URLs or plain data instead.
- **Local imports**: calls into the user's own modules are pickled by reference and fail
  remotely. Inline the needed helpers into the function, or (if the package is published)
  list it in `packages=`.
- **Local files**: paths on this machine do not exist in the sandbox. Pass the data as an
  argument (it is pickled) or have the function download it.
- **Third-party imports**: move them inside the function. Add libraries that are not
  common scientific/ML staples to `packages=` with pinned versions.
- **Return value**: must be picklable and its class importable locally. Prefer plain
  data, NumPy arrays, or DataFrames.
- **Side effects**: an out-of-memory failure is retried once, so writes should be
  idempotent.

## 3. Apply the change

- Add `from readie import remote` and decorate the function. Choose settings from what
  the function does: `memory`/`max_memory` for large data (for example `"4Gi"` /
  `"16Gi"`), `gpu=True` or `gpu_memory` for CUDA work, `timeout` for long jobs.
- If callers are `async`, change them to `await fn.aio(...)`.
- If several calls must share loaded state (a model, a dataset), put them in one
  `Session` and explain that calls in a session run one at a time.
- Keep the edit minimal and match the file's style.

## 4. Verify

- Run any existing tests that call the function. `fn.local(...)` runs it in-process,
  which tests can use to avoid remote calls.
- If the function is self-contained, offer to try it remotely with `run_python` using a
  small script that defines the function, calls it with sample input and prints the
  result.
- Summarize what changed and each hazard you fixed or left for the user.
