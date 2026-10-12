# bookstore-apm

The `bookstore-plugin` from *Mastering AI-Assisted Software Engineering*
(sessions 4 and 5), repackaged as an [APM](https://microsoft.github.io/apm/)
package. One source tree, installed natively into Claude Code, GitHub Copilot
and Codex CLI.

```
bookstore-apm/
├── apm.yml                                   manifest: name, version, targets, MCP server
├── .apm/
│   ├── skills/commit/SKILL.md                exercise 4, task 1 (unchanged)
│   ├── skills/changelog/SKILL.md             exercise 4, task 2 (+ Common Changelog spec)
│   ├── agents/security-auditor.agent.md      exercise 5, task 4 (unchanged)
│   ├── hooks/changelog.json                  exercise 4, task 3, path via ${PLUGIN_ROOT}
│   └── instructions/bookstore-conventions.instructions.md   new: shared rules
├── hooks/run-changelog.py                    the hook script (asks for the bare `changelog` skill)
├── mcp-sqlite/server.py                      exercise 5, task 2, shipped with the package
└── demo/apm-policy.yml                       org policy for the governance beat
```

## Install

In any bookstore project (Go, Python, Kotlin or TypeScript port), with
[`apm`](https://github.com/microsoft/apm#install) on the path:

```sh
apm install RB-Develop/bookstore-apm#v1.0.0 --target claude,copilot,codex
```

Targets can also live in the consumer's `apm.yml` (`targets: [claude, copilot, codex]`),
after which a bare `apm install` is enough.

## What lands where

| Primitive | Claude Code | Copilot | Codex CLI |
|---|---|---|---|
| skills `commit`, `changelog` | `.claude/skills/<name>/` | `.agents/skills/<name>/` | `.agents/skills/<name>/` |
| agent `security-auditor` | `.claude/agents/security-auditor.md` | `.github/agents/security-auditor.agent.md` | `.codex/agents/security-auditor.toml` (`tools` dropped, with a warning) |
| hook PostToolUse → changelog | merged into `.claude/settings.json`; script in `.claude/hooks/bookstore-apm/` | `.github/hooks/bookstore-apm-changelog.json`; script in `.github/hooks/scripts/` | `.codex/hooks.json`; script in `.codex/hooks/bookstore-apm/` |
| instructions | `.claude/rules/bookstore-conventions.md` | `.github/instructions/bookstore-conventions.instructions.md` | `AGENTS.md` section after `apm compile` |
| MCP `sqlite-bookstore` | `.mcp.json` | `.github/mcp.json` | `.codex/config.toml` |

Plus `apm.lock.yaml` with a SHA-256 per deployed file, and the package source
under `apm_modules/RB-Develop/bookstore-apm/` (gitignored by APM).

## Differences from `bookstore-plugin`

- No namespace. The plugin's skills were `/bookstore-plugin:commit`; APM
  installs them as `/commit` and `/changelog`, next to the project's own
  files. The hook script therefore asks for `/changelog`.
- `${CLAUDE_PLUGIN_ROOT}` became `${PLUGIN_ROOT}`. APM rewrites the hook
  command per harness at install time and copies the script along.
- The MCP server is declared in `apm.yml` (`dependencies.mcp`,
  `registry: false`) instead of `.mcp.json`; APM ignores `.mcp.json` on
  install. The command path points at `apm_modules/RB-Develop/bookstore-apm/`,
  so it only works when the package is installed from that GitHub owner.
- `tools: Read, Grep, Glob` on the agent is kept on purpose: Codex cannot
  express it and APM says so at install time. That is the demo's point about
  lossy compilation.
- The conventions instruction file is new; the plugin had no instructions
  primitive.

Verified with APM CLI 0.33.0 on 2026-10-12. `DEMO.md` has the demo runbook.
