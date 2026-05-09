# Upgrade Preparation: v2026.4.30-tangbao.1

## Base

- Official upstream tag: `v2026.4.30`
- Official upstream commit: `73bf3ab1b`
- Tangbao target tag after release approval: `v2026.4.30-tangbao.1`
- Local integration branch: `upgrade/v2026.4.30-tangbao.1`

## Scope

This branch prepares the Tangbao custom release line on top of official Hermes Agent `v0.12.0 / v2026.4.30`.

It retains the currently required Tangbao patches:

1. Discord tool schema Gemini compatibility.
2. `network.safe_intranet_ips` SSRF allowlist.
3. Empty assistant tool-call content normalization for affected Chat Completions APIs.
4. Named custom provider credential precedence.
5. Feishu opt-in LaTeX normalization.

It also includes current Tangbao release notes from `origin/master` through `v2026.4.23-tangbao.3` and the fork management policy document.

## Conflict Resolution Notes

Conflicts resolved during preparation:

- `.gitignore`: kept upstream `models-dev-upstream/` and Tangbao scratch/uv ignore entries.
- `scripts/release.py`: kept upstream author mappings and Tangbao local ops mappings.

## Validation

Run from `/home/openclaw/workspaces/brownie/upgrade-v2026.4.30-tangbao.1` using the branch-local virtual environment.

```bash
.venv/bin/python -m py_compile scripts/release.py
git diff --check
.venv/bin/python -m pytest \
  tests/tools/test_discord_tool.py \
  tests/tools/test_url_safety.py \
  tests/run_agent/test_empty_tool_call_content_normalization.py \
  tests/hermes_cli/test_runtime_provider_resolution.py \
  tests/gateway/test_feishu.py \
  tests/gateway/test_latex_command.py \
  -q
```

Result:

```text
492 passed in 18.32s
```

Mergeability check:

```bash
git merge-tree --write-tree origin/master HEAD
```

Result: exit code `0` after aligning the branch with current `origin/master`.

## Push/PR Status

Brownie's GitHub token cannot push this upgrade branch to the fork because the official 430 upgrade includes workflow file changes and the token lacks GitHub `workflow` scope:

```text
refusing to allow a Personal Access Token to create or update workflow `.github/workflows/contributor-check.yml` without `workflow` scope
```

Direct push to `DongWei-4/hermes-agent` also fails with `403` for Brownie.

Dirty-bun or another account with upstream write access and workflow scope should push the prepared local branch if approved:

```bash
cd /home/openclaw/workspaces/brownie/upgrade-v2026.4.30-tangbao.1
git push origin HEAD:upgrade/v2026.4.30-tangbao.1
```

Then open a PR to `DongWei-4/hermes-agent:master`.

## Production Boundary

This is a development/integration preparation only. Do not update `/home/openclaw/hermes-prod/current`, publish tags, or restart production services from this branch without explicit production authorization.
