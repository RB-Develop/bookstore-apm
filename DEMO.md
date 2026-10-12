# APM demo runbook (day 3, 15–20 min)

Story: "The plugin you built on day 2, now vendor-neutral." Seed is
`bookstore-plugin`; this repo is the same content as an APM package.

Everything below was verified with APM CLI 0.33.0 in a clean consumer on
2026-10-12, except the two items marked *unverified*.

## Tonight: setup (≈30 min)

1. Install APM on the Mac: `brew install apm` (or `pip install apm-cli`).
   Check: `apm --version` → 0.33.0.
2. Publish this repo:
   ```sh
   cd ~/Projects/bookstore-apm
   git init && git add -A && git commit -m "Add bookstore-apm package"
   gh repo create RB-Develop/bookstore-apm --public --source . --push
   git tag v1.0.0 && git push --tags
   ```
   The `apm.yml` MCP path assumes exactly `RB-Develop/bookstore-apm`.
3. Prepare the consumer `~/Projects/bookstore-go`:
   - `go run .` once if `store.db` is missing (it exists now).
   - Commit or stash anything dirty, then make ONE small uncommitted change
     to keep ready for `/commit` (e.g. a comment in `internal/handler/book.go`).
   - Its `CLAUDE.md` is the training-mode "ask one leading question first"
     file. The `/commit` skill says "no leading questions", which usually
     wins, but if Claude starts coaching mid-demo you lose a minute. Safe
     option: `mv CLAUDE.md CLAUDE.md.off` for the demo.
   - `.gitignore` there hides `.claude/skills`, `.claude/agents`,
     `.claude/settings.json`, `.claude/rules`, `.mcp.json`. So `git status`
     will NOT show the Claude side after install. Use `tree -a -I 'apm_modules|.git|worktrees'`
     or `find .claude .agents .codex .github -type f` instead.
4. Full dry run of the demo once (beats 1–3). Take screenshots of each
   terminal state as a wifi fallback.
5. Optional governance beat (needs network + 10 min extra): see beat 4.

## Beat 1: the package (3 min)

```sh
cd ~/Projects/bookstore-apm
tree -a -I .git
cat apm.yml
diff <(cat ~/Projects/ai-assisted-se-claude/ai-assisted-se-claude-exercise/bookstore-plugin/skills/commit/SKILL.md) .apm/skills/commit/SKILL.md && echo "identical"
```

Say: SKILL.md is unchanged, Agent Skills is the standard; APM adds
placement, versioning and policy. Point at `${PLUGIN_ROOT}` in the hook and
at `dependencies.mcp` in `apm.yml`. Instructions are the one primitive the
plugin did not have.

## Beat 2: install into three harnesses (6 min)

```sh
cd ~/Projects/bookstore-go
apm install RB-Develop/bookstore-apm#v1.0.0 --target claude,copilot,codex --dry-run
apm install RB-Develop/bookstore-apm#v1.0.0 --target claude,copilot,codex
```

Read the install log aloud, it is the demo:

- `3 agents integrated -> 3 targets`, `3 hook(s) integrated`, `2 instruction(s)`, `2 skill(s)`
- the three rewritten hook commands (`${CLAUDE_PROJECT_DIR}/.claude/hooks/...`,
  `.codex/hooks/...`, `.github/hooks/scripts/...`)
- `Trusting direct dependency MCP 'sqlite-bookstore'` → configured for Claude, Copilot, Codex
- the warning: **Codex agent: frontmatter field 'tools' was dropped**. This
  is the honest part: compilation is lossy and APM tells you where.
- `Instructions installed for codex. Run 'apm compile' to update AGENTS.md.`

Then show what landed:

```sh
find .claude .agents .codex .github .mcp.json -type f | sort
cat .claude/settings.json          # hook merged, nothing else touched
cat .codex/agents/security-auditor.toml | head -5
head -40 apm.lock.yaml              # sha256 per deployed file
apm compile                         # Codex: conventions into AGENTS.md
```

`apm compile` refuses to overwrite a hand-written `AGENTS.md` ("Protected");
bookstore-go has none, so it generates one. Mention `CLAUDE.md` is left alone:
Claude reads `.claude/rules/` directly.

Then prove it in Claude Code:

```sh
claude
```

- `/help` → `/commit` and `/changelog` are plain project skills, no prefix.
- `/mcp` → `sqlite-bookstore` connected (needs `store.db` in cwd).
- `/commit` on the prepared change → commit → hook fires → `/changelog` runs
  → `CHANGELOG.md` appears. Same flow as the day-2 plugin demo.

Copilot and Codex: show the files, do not run the harnesses live unless
you have tested them tonight. The hook output format (`hookSpecificOutput`
with `additionalContext`) is Claude's; whether Copilot and Codex act on it
is *unverified*. The skills and MCP config are plain files and will load.

## Beat 3: lockfile + audit (2 min)

```sh
sed -i '' 's/Review `git status`/Review git status/' .claude/skills/commit/SKILL.md
apm audit            # drift: hash mismatch on the edited file
apm audit --ci; echo $?   # exit 1: the CI gate
git checkout -- . 2>/dev/null; apm install --force   # restore
```

Say: the lockfile is the supply-chain receipt. Edits under the install
paths are detected; `apm install --frozen` is the CI gate.

## Beat 3b: ship a fix, update the consumer (3 min)

Story: `v1.0.0` has a real bug. Copilot rejects the agent because
`tools: Read, Grep, Glob` is Claude's comma-string form and Copilot needs a
YAML array. `v1.0.1` fixes it (`tools: [Read, Grep, Glob]`).

```sh
cd ~/Projects/bookstore-go
head -6 .github/agents/security-auditor.agent.md      # broken: tools: Read, Grep, Glob
apm outdated                                           # read-only: v1.0.0 -> v1.0.1, status "outdated"
apm install RB-Develop/bookstore-apm#v1.0.1 --target claude,copilot,codex
head -6 .github/agents/security-auditor.agent.md      # fixed: tools: [Read, Grep, Glob]
```

Say: `apm outdated` only compares the lockfile with the remote tags and
installs nothing. The lockfile pins the commit, so the upgrade is an explicit, reviewable
diff, not a surprise.

## Beat 4 (optional): org policy blocks a foreign dependency (4 min)

Constraint: at install time APM discovers policy only from the consumer's
git remote owner (`<owner>/.github` repo, file `apm-policy.yml`). No local
override during install. To run it live:

1. Create public repo `RB-Develop/.github` with `demo/apm-policy.yml` from
   this repo at its root.
2. `cd ~/Projects/bookstore-go && git remote add origin git@github.com:RB-Develop/bookstore-go.git`
   (the repo does not need to exist; only the URL is parsed).
3. `apm policy status` → Outcome `found`, Enforcement `block`.
4. `apm install github/awesome-copilot/agents/api-architect.agent.md` → refused
   before any file is written. `apm install RB-Develop/bookstore-apm#v1.0.0` → allowed.

Offline fallback for the same story (verified):

```sh
apm policy status --policy-source ~/Projects/bookstore-apm/demo/apm-policy.yml
```

Shows the parsed policy (3 allow patterns, enforcement block) without
needing the `.github` repo. Say the live refusal, show the file.

## Deciding questions (3 min)

Back to their layer-4 roadmap line. APM earns its slot if one holds:

1. A second harness exists or is coming (Copilot in IntelliJ, Cursor,
   analysts on Copilot). One source → native files per harness.
2. Code not on GitHub (Azure DevOps, GitLab). Marketplaces are GitHub-shaped;
   APM deps are any git URL.
3. Governance: lockfile hashes, `apm audit --ci`, org `apm-policy.yml`
   enforced before files hit disk.

If none applies: say so, plugins + marketplace already cover a Claude-only org.

## Gotchas found while building this

- `apm install` also accepts the **unchanged** `bookstore-plugin` folder
  (`package_type: marketplace_plugin`) and deploys skills, agent and hook to
  all three targets. Only `.mcp.json` is ignored. Good one-liner for the
  room: "your plugin was already an APM package, minus the MCP server."
- `${PLUGIN_ROOT}` is rewritten in hook commands only, not in MCP args.
  Hence the literal `apm_modules/RB-Develop/bookstore-apm/...` path.
- `apm pack` writes `.github/plugin/plugin.json` into the package source
  tree (gitignored here) and its bundle omits the hook script and
  `mcp-sqlite/`. Not a demo beat.
- GitHub fetches need auth or a public repo; keep the package public.
- Docs site (microsoft.github.io/apm) was unreachable at times on 2026-10-09
  and 2026-10-12. Do not plan to open it live.
