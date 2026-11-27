# Readie plugin for Claude

This plugin connects Claude to [Readie](https://readie.org), a serverless platform
that runs Python functions in gVisor sandboxes restored from pre-built checkpoints.
With the plugin installed, Claude can run Python on Readie and see what it prints. It
can also add the `@remote` decorator from the `readie` SDK to functions in your code,
and explain Readie errors.

## Install

In Claude Code:

```text
/plugin marketplace add readie-project/plugins
/plugin install readie@readie
```

In Claude chat (claude.ai, the desktop app and the mobile apps), add the MCP server as a
custom connector. Open **Customize**, then **Connectors**, select **Add**, then **Add
custom connector**. Enter the URL `https://run.readie.org/mcp`, and select **No sign-in**
for authentication.

## What it adds

| Component | Name | What it does |
| --------- | ---- | ------------ |
| MCP tool | `run_python` | Runs Python source on Readie and returns its printed output, duration and errors. Accepts the same options as `@remote`: `packages`, `memory`, `max_memory`, `gpu`, `gpu_memory`, `max_gpu_memory`, `timeout`, `session`, `disable_optimized_execution`, `checkpoint_id`. |
| MCP tool | `new_session` | Returns a new random session id, so that several `run_python` calls can share Python state. |
| Skill | `readie` | Loads automatically when you work with Readie or the `readie` SDK. It covers the SDK, its limits and its errors. |
| Command | `/readie:run <file or code>` | Runs a file or snippet on Readie. |
| Command | `/readie:offload <function>` | Converts a function in your code to run on Readie with `@remote`. |

When the plugin is installed in Claude chat, the commands are not slash commands. Claude
applies them as skills when a request fits. The skills need code execution to be turned
on in Claude's settings. Claude chat limits how long one tool call can run, so run long
executions from Claude Code or the Python client.

## Data and network use

- The plugin connects Claude to the hosted Readie MCP server at
  `https://run.readie.org/mcp`. The plugin contains no server code and installs nothing.
- `run_python` sends the code you ask it to run, together with its options, to that server
  over HTTPS. The code runs on the Readie service, and the server returns its printed
  output. No account or token is needed.
- `new_session` asks the server for a random session id. Session ids are not tied to a
  user. Anyone who knows a session id can run code in that session, so do not keep
  secrets in session state.
- The server limits requests per client address and the size of the code and output.
- The skills do not use the network. `/readie:offload` runs `python --version` and
  `python -c "import readie"` on your machine to check the local setup.

## Links

- Documentation: https://readie.org/docs
- Plugin guide: https://readie.org/docs/guides/claude-code
- Plugin source and issues: https://github.com/readie-project/plugins
- Readie source: https://github.com/readie-project/readie
- Privacy policy: https://readie.org/privacy

Licensed under Apache-2.0.
