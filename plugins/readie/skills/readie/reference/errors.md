# Readie errors: cause and fix

Condensed from https://readie.org/docs/guides/errors and
https://readie.org/docs/guides/troubleshooting. All exceptions inherit from
`readie.ReadieError`.

## Diagnose in this order

1. Read the exception class and message. The class alone usually names the cause.
2. For `RemoteExecutionError`, read `remote_traceback` (it is in the message): the bug
   is in the user's function. Reproduce with `fn.local(...)`.
3. For `ExecutionError` subclasses, the last 40 lines of remote output are in the
   message. Package-install output from `uv` appears there too.

## Setup and usage (raised locally, nothing was sent)

| Exception | Cause | Fix |
| --------- | ----- | --- |
| `IncompatiblePythonError`: `Readie requires Python 3.12, found Python 3.x` | Local interpreter is not 3.12. | `uv venv --python 3.12` and run from it. |
| `ConfigurationError` | Bad size (`"1.5Gi"`, negative), `max_memory` below `memory`, non-positive `timeout`, or `checkpoint_id` with `disable_optimized_execution=True`. | Fix the value. |
| `InvalidPackageError` | A `packages=` entry is not a valid requirement string. | Fix the spelling or specifier. |
| `SerializationError`: `cannot serialise call to ...` | An argument or closed-over object cannot be pickled (file, socket, connection, lock, thread). | Create the object inside the function; pass paths or plain data instead. |
| `SerializationError`: `cannot deserialise the result ...` | The return value's class is not importable locally, or library versions differ. | Return plain data, or install the same library version locally. |
| `ClientClosedError` | A closed `Client` or `Session` was reused. | Create a new one. |
| `BlockingCallInEventLoopError` | `fn(...)` called inside a running event loop. | `await fn.aio(...)`. |

## Transport (`TransportError`, has `.code` = gRPC status name)

| Exception | Cause | Fix |
| --------- | ----- | --- |
| `ClusterUnavailableError` (`UNAVAILABLE`) | Network problem, or the service is down or has no free worker. | Check connectivity to the internet (outbound HTTP/2); retry later. |
| `PermissionDeniedError` (`UNAUTHENTICATED`/`PERMISSION_DENIED`) | Missing or wrong token. | `export READIE_AUTH_TOKEN=...` before the client is created. It cannot be passed in code. |
| `RemoteTimeoutError` (`DEADLINE_EXCEEDED`) | The call exceeded `timeout`. | Raise or remove `timeout`. |
| `InvalidRequestError` (`INVALID_ARGUMENT`/`FAILED_PRECONDITION`) | Package install failed (`could not install the requested packages`; `uv` output precedes it), unknown `checkpoint_id`, or `disable_optimized_execution` on a restored session. | For installs: fix the name/version, read the `uv` lines. Otherwise correct the request. |
| `ResourceExhaustedError` | No worker has room, the session stayed busy too long, or a message was too large. | Retry later, request less memory, or use more sessions. |
| `SessionExpiredError` (`NOT_FOUND`) | The session's sandbox was removed after idling. | Open a new session; its state is lost. |
| `ExecutionCancelledError` | The call was cancelled. | Retry if unintended. |

## Execution (`ExecutionError`: has `logs`, `worker_id`, `container_id`)

| Exception | Cause | Fix |
| --------- | ----- | --- |
| `RemoteExecutionError` | The function raised remotely. `remote_type`, `remote_message`, `remote_traceback`. The original exception object is not rebuilt, so `except ValueError` will not catch it. | Fix the function. `ModuleNotFoundError` here usually means a missing `packages=` entry or a local module that was not shipped. |
| `EmptyResultError` | No result came back; often an out-of-memory kill. | Set a larger `memory`/`max_memory`; check `logs`. |

## Out of memory

There is no dedicated exception. A call that dies without a result is retried once with
more memory if `max_memory` allows; if the retry fails, the original error surfaces.
Fix with `@remote(memory="4Gi", max_memory="16Gi")`.

## The `run_python` tool

Its errors are HTTP-level: `HTTP 422` means an invalid option (the message says which),
`HTTP 413` means the code is too large, `HTTP 429` means too many runs from this
address. A run that started but failed shows `Failed after ...` with the traceback in
the output.
