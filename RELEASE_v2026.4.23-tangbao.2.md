# Hermes Agent v2026.4.23-tangbao.2

**Base Version:** v0.11.0 (Official)
**Release Date:** April 25, 2026
**Planned Git Tag:** `v2026.4.23-tangbao.2`

> 本版本是基于官方 **v0.11.0** 与糖包定制版前序版本的稳定性修复版，重点修复 Claude / Gemini OpenAI-compatible Chat Completions 端点在历史工具调用消息回放时的兼容性问题，并补齐 PR 质量门禁，便于后续版本发布前自动检查。

---

## 🐛 Bug Fixes

- **Assistant tool-call empty content compatibility** — 修复历史 assistant `tool_calls` 消息带 `content: ""` 时，部分 OpenAI-compatible Chat Completions 端点返回 500 的问题。现在针对已知受影响路由（`custom:jingua-fengxinzi` / `https://gua.guagua.uk/v1` / Google Gemini OpenAI-compatible endpoint）仅在 outgoing API copy 层将空字符串规范化为 `null`，不会修改持久化会话历史。([personal#7](https://github.com/DongWei-4/hermes-agent/pull/7), [issue#5](https://github.com/DongWei-4/hermes-agent/issues/5))

---

## 🏗️ Release / CI

- **Master PR quality gate** — 新增 master 方向 PR 的质量门禁与贡献者归因检查，用于在合并前捕获 release-note attribution、供应链风险和 Nix lockfile 问题。([personal#6](https://github.com/DongWei-4/hermes-agent/pull/6))

---

## ✅ Validation

- Regression coverage added for provider-scoped outgoing-only normalization.
- Targeted verification completed before merge of the bugfix PR:

```text
PYTHONPATH=. /home/openclaw/dev/hermes-agent/.venv/bin/python -m pytest \
  tests/run_agent/test_empty_tool_call_content_normalization.py \
  tests/run_agent/test_dict_tool_call_args.py \
  tests/agent/transports/test_chat_completions.py -q

48 passed
```

---

## 👥 Contributors

- **@DongWei-4** — 糖包定制版维护与发布把关
- **@dirty-bun-ops** — 生产问题定位、复现矩阵和发布评审
- **@brownie-ops** — bugfix implementation and regression coverage

---

## 🏷️ Tagging Plan

After this release-note PR is merged into `master`, create and push the annotated tag on the resulting master commit:

```bash
git fetch origin master --tags
git checkout master
git pull --ff-only origin master
git tag -a v2026.4.23-tangbao.2 -m "Hermes Agent v2026.4.23-tangbao.2"
git push origin v2026.4.23-tangbao.2
```

**Full Changelog**: [v2026.4.16-tangbao.1...v2026.4.23-tangbao.2](https://github.com/DongWei-4/hermes-agent/compare/v2026.4.16-tangbao.1...v2026.4.23-tangbao.2)
