# readie SDK reference (condensed)

Condensed from https://readie.org/docs/guides/sdk and
https://readie.org/docs/getting-started/packages-and-resources. Those pages are
authoritative if anything here disagrees.

## Install

```bash
uv venv --python 3.12
uv pip install readie        # or: pip install readie / uv add readie
export READIE_AUTH_TOKEN=... # only if the service requires a token
```

The hosted service is the default; no server address is needed.

## `remote`

```python
remote(func=None, /, *, client=None, timeout=None, session=None, gpu=False,
       memory=None, max_memory=None, gpu_memory=None, max_gpu_memory=None,
       packages=None, disable_optimized_execution=False, checkpoint_id=None)
```

Used bare (`@remote`) or with keywords (`@remote(memory="2Gi")`). Decorating opens no
connection; bad sizes or package strings raise at decoration time.

| Keyword | Meaning |
| ------- | ------- |
| `timeout` | Seconds for one call. |
| `session` | A `Session`; calls in it share a warm sandbox and its Python state. |
| `gpu` | Send the call to a GPU worker. |
| `memory` / `max_memory` | Starting memory and the ceiling it may grow to. |
| `gpu_memory` / `max_gpu_memory` | GPU memory and its ceiling. Implies `gpu=True`. |
| `packages` | PEP 508 requirements installed before **every** call (no cache). Entries the sandbox image already has are skipped, whatever version they pin. |
| `disable_optimized_execution` | Start cold; never restore a checkpoint. |
| `checkpoint_id` | Restore exactly this checkpoint. Cannot be combined with the previous one. |

Sizes are `int` bytes or whole-number strings: `"512Mi"`, `"4Gi"` (powers of 1024),
`"2G"` (powers of 1000). `"1.5Gi"` and negatives are rejected. A ceiling below its
starting value raises `ConfigurationError`.

## `RemoteFunction` (what `@remote` returns)

| Member | Behaviour |
| ------ | --------- |
| `fn(*a, **kw)` | Run remotely and block. |
| `await fn.aio(*a, **kw)` | Run remotely without blocking. Required inside an event loop. |
| `fn.local(*a, **kw)` | Run in-process: no remote call, no pickling. |
| `fn.bind(session=None, *, client=None, timeout=None)` | Copy bound to a session, client or timeout. |
| `fn.func` | The undecorated function. |

Methods can be decorated; the instance is pickled as the first argument. A successful
call prints `Execution completed in <s>s` to stdout; the function's own output is
written to stderr.

## Sessions

```python
from readie import Session, remote

with Session() as s:
    load = remote(load_model, session=s, memory="4Gi")
    predict = remote(run_inference, session=s)
    load("bert-base")
    predict("hello")  # same sandbox, model still in memory
```

Calls in one session run one at a time; a call waiting too long on a busy session fails
with `ResourceExhaustedError`. An idle session expires after a few minutes, then raises
`SessionExpiredError`; open a new one. Calls in a session are never retried.

## `Client`, `configure`, `Settings`

- `Client(settings=None, ...)` checks the Python version at construction. Channels
  connect on first use. It is a context manager (`with` / `async with`).
- `client.session(session_id=None)` yields a `Session`.
- `configure(**settings)` replaces the process-wide default client;
  `default_client()` returns it; `reset()` closes it.
- `Settings` fields: `timeout` (seconds or `None`), `chunk_size`, `stream_logs`
  (bool). `auth_token` is read only from `READIE_AUTH_TOKEN`.

## Pickling checklist

- Serialises: plain functions, lambdas, closures over ordinary values, classes,
  dataclasses, NumPy arrays, pandas frames.
- Does not: open files, sockets, DB connections, locks, threads, generators bound to
  local resources. Create them inside the function.
- Functions from importable local modules are pickled **by name** and fail remotely.
  Functions defined in `__main__` (a script or notebook) are pickled by value and work.
- Imports inside the function resolve in the sandbox. Libraries missing there go in
  `packages=`.
- Local and sandbox Python must both be 3.12; library versions used in arguments or
  results should match too.

## Minimal example

```python
from readie import remote


@remote(memory="2Gi", packages=["httpx==0.27.2"])
def fetch_sizes(urls: list[str]) -> dict[str, int]:
    import httpx

    return {u: len(httpx.get(u, timeout=10).content) for u in urls}


if __name__ == "__main__":
    print(fetch_sizes(["https://example.com"]))
```
