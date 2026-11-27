# Readie plugins

This repository holds the plugins that connect AI coding agents to
[Readie](https://readie.org), a serverless platform that runs Python functions in
gVisor sandboxes restored from pre-built checkpoints. It is a plugin marketplace for
Claude Code. It holds one plugin, [`readie`](plugins/readie/), which lets Claude Code
run Python on Readie, add the `@remote` decorator from the `readie` SDK to functions in a
project, and explain Readie errors.

## Install

```text
/plugin marketplace add readie-project/plugins
/plugin install readie@readie
```

[`plugins/readie/README.md`](plugins/readie/README.md) lists what the plugin adds
and what it sends over the network. The user guide is at
https://readie.org/docs/guides/claude-code.

## Layout

| Path | Purpose |
| ---- | ------- |
| `.claude-plugin/marketplace.json` | The Claude Code marketplace. Lists every plugin under `plugins/` |
| `plugins/<name>/` | One plugin per folder, exactly as users install it and as it is submitted to a plugin directory |
| `plugins/readie/.claude-plugin/plugin.json` | Manifest: name, version, declared network hosts. `icon.png` sits beside it |
| `plugins/readie/.mcp.json` | Points Claude Code at the hosted MCP server, `https://run.readie.org/mcp` |
| `plugins/readie/skills/` | `readie` (loads automatically, with `reference/sdk.md` and `reference/errors.md`), `run` and `offload` |
| `scripts/check_marketplace.py` | Fails when a plugin folder and the marketplace disagree |
| `Makefile`, `.github/workflows/ci.yml` | `make validate`, which CI runs on every push and pull request |

Each plugin folder is self-contained: no symlinks, no paths outside it, and no code to
install. A plugin directory reviews one folder at a time, so a plugin must not depend on
files outside its own folder.

## Design

- The plugins hold no server code. The MCP server is the `/mcp` route of the playground
  service in the Readie repository (`playground/src/readie_playground/mcp_server.py`),
  served at `https://run.readie.org/mcp`. It shares its request model, checks, rate limit
  and runner with the HTTP execution endpoint, and its tests live there.
- The skills hold the knowledge that a plugin adds: when to use each tool, and the rules
  of the `readie` SDK. Their text does not depend on Claude Code, so a plugin for another
  agent can reuse it.
- The skills' `reference/*.md` files condense the site's SDK, errors and troubleshooting
  pages. Update them when those pages change, and update the skills that mention a tool
  when the tools change in the Readie repository.

## Develop

```bash
make validate
```

`make validate` checks that the marketplace lists every folder under `plugins/`, runs
`claude plugin validate --strict` on each plugin, and validates the marketplace. It needs
`python3` and the `claude` CLI.

Load the plugin in a session without installing it, and run `/reload-plugins` after
each edit:

```bash
claude --plugin-dir plugins/readie
```

To try the MCP route of a local Readie stack, add it to the session as a second server.
The plugin's own server still points at `https://run.readie.org/mcp`:

```bash
claude --plugin-dir plugins/readie --mcp-config '{"mcpServers": {"readie": {"type": "http", "url": "http://localhost:50051/playground/mcp"}}}'
```

## Add a plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`, a `README.md` of at least
   40 words, and a copy of `LICENSE`. Copy files instead of linking them, because plugin
   directories reject symlinks.
2. Add an entry to `.claude-plugin/marketplace.json` with `"source": "./plugins/<name>"`
   and the same `name` as the manifest.
3. Run `make validate`. It fails until both steps are done.

## Support another agent

Each agent reads its own marketplace file and plugin manifest. To support another
agent, add its marketplace file at the path that agent reads, and give each plugin the
manifest and MCP configuration that agent expects. For example, Codex reads
`.agents/plugins/marketplace.json`. Reuse the skills, and point the MCP configuration
at `https://run.readie.org/mcp`. Extend `scripts/check_marketplace.py` and `make
validate` to cover the new files.

Users of every agent then add the same repository, and the skills stay in one place.
If a plugin for one agent ends up sharing nothing with the others, move it to its own
repository. A marketplace entry can install a plugin from another repository, or from a
subfolder of one, so the install command does not have to change.

## Release

1. Bump `version` in the plugin's `.claude-plugin/plugin.json`. Installed copies skip an
   update whose version has not changed.
2. Run `make validate`.
3. Merge to `main`. Users get the update with `/plugin marketplace update readie`.
4. For Anthropic's plugin directory, submit or update at claude.ai/directory/manage. Point
   it at the plugin's folder, for example `plugins/readie`, and run its **Validate** step
   first. The listing icon comes from `.claude-plugin/icon.png`, and it is taken only on
   the first submission.

## License

Apache-2.0. See [`LICENSE`](LICENSE).
