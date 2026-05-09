# Tangbao Custom Fork Management

This document defines how the Tangbao custom release line follows upstream Hermes Agent while preserving household-specific patches. It is intentionally strict: internal PRs that violate these rules should be blocked until corrected.

## Goals

- Keep production safe and reproducible.
- Minimize long-lived divergence from upstream.
- Make every Tangbao customization auditable, testable, and droppable when upstream supersedes it.
- Separate upstream synchronization, custom patch maintenance, release notes, and production deployment.

## Repository Model

Treat the fork as:

```text
upstream tag/main
  -> Tangbao integration branch
  -> small feature/fix branches
  -> Tangbao custom release tag
```

Do not treat the fork as an unstructured permanent divergence.

### Branch Layers

| Layer | Example | Purpose | Rules |
|---|---|---|---|
| Upstream baseline | `upstream-v2026.4.30` / upstream tag | Exact official source | Never edit. Only fetch/verify. |
| Upgrade integration | `upgrade/v2026.4.30-tangbao.1` | Replay selected Tangbao patches onto a new upstream base | May contain retained custom patches and upgrade docs only. |
| Feature/fix branch | `fix/custom-provider-key-precedence` | One logical custom change | Small, reviewed, tested, and independently droppable. |
| Release prep | `release/v2026.4.30-tangbao.1-prep` | Release notes and planned tag instructions | No functional code changes unless explicitly approved. |
| Production | `/home/openclaw/hermes-prod/current` | Live household runtime | Read-only to Brownie unless explicitly authorized. |

## Patch Queue Discipline

Every Tangbao customization must have a patch record. The record should answer:

- What problem does this solve?
- Which commit(s) implement it?
- Which tests prove it?
- Has upstream fixed it?
- What is the drop condition?
- Is this household-specific or suitable for upstream PR?

Use this status taxonomy during every upstream upgrade:

| Status | Meaning | Required action |
|---|---|---|
| `keep` | Upstream has not fixed it | Replay/adapt patch and run tests. |
| `drop` | Upstream fully supersedes it | Remove from patch queue and document why. |
| `adapt` | Upstream partly overlaps or changed nearby code | Rewrite patch minimally on new base. |
| `upstream-pr` | Should be contributed upstream | Keep locally until upstream merges; then reassess as `drop`. |
| `hold` | Risk or unclear behavior | Do not ship production release until resolved. |

## Upgrade Workflow

For a new official release, use a fresh integration branch/worktree:

```bash
git fetch --prune --tags upstream
git worktree add ~/workspaces/brownie/upgrade-vYYYY.M.D-tangbao.N \
  -b upgrade/vYYYY.M.D-tangbao.N upstream-vYYYY.M.D
```

Then:

1. Verify the official tag and release notes.
2. Create/update the Tangbao patch record.
3. Replay only retained custom patches, preferably one commit per logical patch.
4. Resolve conflicts in favor of upstream unless the Tangbao patch explicitly requires otherwise.
5. Run targeted tests for every retained patch.
6. Run smoke tests for provider routing, gateway, tool schemas, URL safety, and release scripts when touched.
7. Produce an upgrade report before release prep.
8. Prepare release notes in a separate release-prep commit/PR.
9. Do not update production or publish tags from Brownie without explicit authorization.

## Review Gate for Internal PRs

Brownie should reject internal PRs directly when any of these are true:

- The PR modifies production checkout paths or assumes production is writable.
- Functional changes are mixed with release-note-only changes without a clear reason.
- A Tangbao patch lacks tests or a documented verification path.
- A patch duplicates upstream behavior without explaining why it is still needed.
- A change broadens SSRF/private-network access without explicit allowlist semantics and tests.
- Secrets, tokens, or profile-private data are committed or printed in logs.
- The PR has unresolved merge conflicts with the current upstream target.
- The PR changes broad/core files without a small-scope rationale and targeted tests.
- The PR is not independently droppable or mixes unrelated concerns.

Approval requires:

- Clear problem statement.
- Minimal diff.
- Relevant tests or a documented reason tests are not possible.
- Compatibility note against the current upstream base.
- Rollback/drop condition for Tangbao-specific behavior.

## Release and Versioning Rules

Tangbao custom tags use:

```text
v<official-base-date>-tangbao.<sequence>
```

The date is the official upstream base date, not the day the release is prepared. Example: the first Tangbao custom release based on official `v2026.4.30` is:

```text
v2026.4.30-tangbao.1
```

Use the wording **Tangbao custom release** / **糖包定制版**. Do not describe this release line as a Dirty-bun series.

## Current v2026.4.30 Patch Assessment

As of the official `v2026.4.30 / v0.12.0` assessment:

| Patch | Status | Notes |
|---|---|---|
| Discord tool schema Gemini compatibility | `keep` | Upstream still exposes `auto_archive_duration` as an integer enum. |
| `network.safe_intranet_ips` SSRF allowlist | `keep` | Upstream has SSRF fixes but not this explicit configured allowlist. |
| Empty assistant tool-call content normalization | `keep` | Upstream has many provider/tool-call fixes but not this route-specific API normalization. |
| Named custom provider credential precedence | `keep` | Upstream still checks the base-url credential pool before the named provider's own credentials. |
| Feishu opt-in LaTeX normalization | `keep` | Upstream has general Markdown/LaTeX work, but no Feishu outbound normalization toggle. |

## Production Boundary

Brownie may prepare branches, tests, reports, and PRs. Production release, rollback, service restart, or tag publication belongs to Dirty-bun or requires explicit user authorization.
