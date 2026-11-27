---
name: readie
description: Use Readie, the checkpoint/restore serverless platform for Python. Covers running Python on Readie with the run_python tool, and writing, porting and debugging code that uses the readie SDK (@remote, Client, Session, packages=, memory budgets, GPUs).
when_to_use: The user mentions Readie, readie.org, `from readie import remote`, `@remote`, or a Readie exception (RemoteExecutionError, SerializationError, IncompatiblePythonError, ClusterUnavailableError, SessionExpiredError, InvalidRequestError, PermissionDeniedError); asks to run Python "on Readie" or "remotely in a sandbox"; or wants to offload a slow or memory-heavy Python function.
---

# Readie

Readie runs Python functions in gVisor sandboxes restored from pre-built checkpoints,
so heavy imports such as `torch` or `pandas` are already loaded when the call starts.
Two ways in:

| Goal | Use |
| ---- | --- |
| Run a script now and see what it prints | The `run_python` tool from this plugin. No install, no token. |
| Make a function in the user's code run on Readie | The `readie` SDK: `@remote` on the function. |

## Running code with `run_python`

- The code runs **as a script** on the hosted service. Only printed output returns:
  `print()` every value you need. A bare expression such as `1 + 1` prints nothing.
- The code leaves the user's machine. Do not send secrets, credentials, tokens, or
  private data. If the code would need them, stop and tell the user instead.
- Local files and local modules do not exist in the sandbox. Inline what the script
  needs, or install public packages with `packages=["name==version"]`.
- Common libraries are preinstalled. Pin versions in `packages` for repeatable results;
  a package the sandbox already has is skipped whatever version is asked for.
- Resources: `memory="2Gi"`, `max_memory="8Gi"`, `gpu=true`, `gpu_memory="16Gi"`,
  `timeout` in seconds. Sizes are whole numbers: `"1.5Gi"` is rejected, use `"1536Mi"`.
- State across calls: call `new_session`, then pass the same `session` id to each
  `run_python` call, one call at a time. Idle sessions expire after a few minutes;
  start a new one and rebuild state if a call reports the session expired.
- A result marked as failed carries the remote traceback in its output. Read it before
  retrying. "Too many runs" means the endpoint rate limit: wait a minute.

## Writing code with the SDK

Read `reference/sdk.md` before writing or changing `@remote` code, and
`reference/errors.md` when the user shows a Readie exception or traceback. The rules
that cause most failures:

1. **Python 3.12 exactly.** The client refuses any other minor version
   (`IncompatiblePythonError`), because functions are cloudpickled locally and
   unpickled by Python 3.12 in the sandbox.
2. **Everything crossing the wire must pickle.** Arguments, return values and
   closed-over objects. Open files, sockets, DB connections, locks and threads do not:
   create them inside the function.
3. **Local modules are not shipped.** A function imported from the user's own package
   is pickled by reference and fails to import remotely. Put the logic in the decorated
   function (or a script/notebook-level function), or publish the package and list it in
   `packages=`.
4. **Imports go inside the function** when the library is only needed remotely, so the
   local machine does not need it installed.
5. **Return classes must be importable locally**, since the result is unpickled there.
6. **Memory**: the default budget is small. Set `memory=` and a larger `max_memory=` for
   data-heavy work. A suspected out-of-memory failure is retried once, so a function can
   run twice: keep side effects idempotent.
7. **Async code** must use `await fn.aio(...)`; a blocking call inside a running event
   loop raises `BlockingCallInEventLoopError`.
8. **Auth**: the client sends `READIE_AUTH_TOKEN` from the environment when it is set.
   Never write a token into source code.

`fn.local(...)` runs the undecorated function in-process, which is the quickest way to
separate a bug in the function from a Readie problem.

Authoritative docs: https://readie.org/docs (SDK reference at
https://readie.org/docs/guides/sdk).
