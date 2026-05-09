# Hermes Agent v2026.4.23-tangbao.3

**Release type:** 糖包定制版
**Base version:** v0.11.0 (official 2026.4.23 line)
**Release date:** 2026-04-26
**Planned Git tag:** `v2026.4.23-tangbao.3`

> Versioning note: the leading date follows the upstream official base version date. This is the third Tangbao custom release based on the official `2026.4.23` line.

## Summary

This release contains one targeted bug fix after `v2026.4.23-tangbao.2`.

## Bug Fixes

- Fixed custom provider credential resolution when multiple `custom_providers` share the same `base_url` but use different API keys.
  - Explicit `custom:<name>` provider selection now preserves that named provider's own credentials.
  - Runtime resolution checks `explicit_api_key`, `key_env`, and inline `api_key` before falling back to a shared `base_url` credential pool.
  - Existing pool fallback behavior is preserved when the named provider has no usable key.

## Validation

- `python -m pytest tests/hermes_cli/test_runtime_provider_resolution.py -q`
- `python -m pytest tests/agent/test_credential_pool.py tests/hermes_cli/test_runtime_provider_resolution.py -q`

## Contributors

- Brownie
- Dirty-bun

## Post-merge tag command

After this release note is merged, create the annotated tag from the updated upstream `master`:

```bash
git fetch origin master --tags
git checkout master
git pull --ff-only origin master
git tag -a v2026.4.23-tangbao.3 -m "Hermes Agent v2026.4.23-tangbao.3"
git push origin v2026.4.23-tangbao.3
```
