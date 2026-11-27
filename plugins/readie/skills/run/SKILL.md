---
name: run
description: Run a Python file or snippet on Readie with the run_python tool and report what it prints. Use when the user asks to run a script or a piece of Python code on Readie.
argument-hint: "<file.py | python code> [--memory 2Gi] [--gpu] [--packages a==1,b==2]"
disable-model-invocation: true
---

# Run on Readie

Run the file or code that the user names on Readie, with the `run_python` tool from the
readie MCP server. When this skill runs as the `/readie:run` command, the user's
argument is: `$ARGUMENTS`.

1. Work out the code:
   - If the user names a `.py` file that you can read, read it. In a coding agent this is
     a file in the project. In Claude chat it is a file that the user attached.
   - Otherwise treat the code in the message as Python source.
   - If there is no code, ask which file or code to run.
2. Check it before sending, because the code leaves the user's machine:
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
