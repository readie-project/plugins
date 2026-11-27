---
name: run
description: Run a Python file or snippet on Readie with the run_python tool and report what it prints.
argument-hint: "<file.py | python code> [--memory 2Gi] [--gpu] [--packages a==1,b==2]"
disable-model-invocation: true
---

# Run on Readie

Run `$ARGUMENTS` on Readie with the `run_python` tool from the readie MCP server.

1. Work out the code:
   - If the argument is a path to an existing `.py` file, read it.
   - Otherwise treat the argument as Python source.
   - With no argument, ask which file or code to run.
2. Check it before sending, because the code leaves this machine:
   - If it contains secrets, tokens, passwords or private data, stop and tell the user.
   - If it imports a local module or reads a local file, it will fail remotely. Say so,
     and offer to inline the module or embed the data.
   - Only printed output comes back. If the code ends in a bare expression, wrap it in
     `print()`. An `if __name__ == "__main__":` block runs as usual.
3. Map flags to tool arguments: `--memory` → `memory`, `--max-memory` → `max_memory`,
   `--gpu` → `gpu: true`, `--gpu-memory` → `gpu_memory`, `--packages` → `packages`
   (split on commas), `--timeout` → `timeout`, `--cold` →
   `disable_optimized_execution: true`. Add third-party imports that are unlikely to be
   preinstalled to `packages` with a pinned version.
4. Call `run_python` once. Show the output verbatim in a code block and the duration.
5. On failure, explain the cause from the traceback in one or two sentences and propose
   a fix (see the `readie` skill's `reference/errors.md`). Do not rerun automatically
   unless the fix is only a resource or package change; then rerun once and say so.
