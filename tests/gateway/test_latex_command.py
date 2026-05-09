"""Tests for gateway /latex command and Feishu LaTeX normalization toggling."""

import asyncio
from types import SimpleNamespace

import yaml

import gateway.run as gateway_run
from gateway.config import Platform
from gateway.platforms.base import MessageEvent
from gateway.session import SessionSource


def _make_event(text="/latex", platform=Platform.FEISHU, user_id="ou_user", chat_id="oc_chat"):
    source = SessionSource(
        platform=platform,
        user_id=user_id,
        chat_id=chat_id,
        user_name="testuser",
    )
    return MessageEvent(text=text, source=source)


def _make_runner():
    runner = object.__new__(gateway_run.GatewayRunner)
    runner.adapters = {}
    return runner


class TestLatexCommand:
    def test_latex_is_in_gateway_known_commands(self):
        from hermes_cli.commands import GATEWAY_KNOWN_COMMANDS

        assert "latex" in GATEWAY_KNOWN_COMMANDS

    def test_feishu_adapter_default_keeps_latex_unchanged(self):
        from gateway.config import PlatformConfig
        from gateway.platforms.feishu import FeishuAdapter

        adapter = FeishuAdapter(PlatformConfig())

        assert adapter.format_message(r"公式 \(\alpha \leq y\)") == r"公式 \(\alpha \leq y\)"

    def test_feishu_adapter_config_can_enable_latex_normalization(self):
        from gateway.config import PlatformConfig
        from gateway.platforms.feishu import FeishuAdapter

        adapter = FeishuAdapter(PlatformConfig(extra={"latex_normalization_enabled": True}))

        assert adapter.format_message(r"公式 \(\alpha \leq y\)") == "公式 α ≤ y"

    def test_feishu_adapter_legacy_config_name_can_enable_latex_normalization(self):
        from gateway.config import PlatformConfig
        from gateway.platforms.feishu import FeishuAdapter

        adapter = FeishuAdapter(PlatformConfig(extra={"latex_normalization": True}))

        assert adapter.format_message(r"公式 \(x \to y\)") == "公式 x → y"

    def test_feishu_adapter_live_toggle_updates_formatting(self):
        from gateway.config import PlatformConfig
        from gateway.platforms.feishu import FeishuAdapter

        adapter = FeishuAdapter(PlatformConfig())
        assert adapter.format_message(r"公式 \(x \to y\)") == r"公式 \(x \to y\)"

        adapter.set_latex_normalization_enabled(True)
        assert adapter.format_message(r"公式 \(x \to y\)") == "公式 x → y"

    async def _run_latex_command(self, tmp_path, monkeypatch, command):
        hermes_home = tmp_path / "hermes"
        hermes_home.mkdir()
        config_path = hermes_home / "config.yaml"
        config_path.write_text(
            "platforms:\n"
            "  feishu:\n"
            "    enabled: true\n"
            "    extra:\n"
            "      app_id: cli_xxx\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(gateway_run, "_hermes_home", hermes_home)

        runner = _make_runner()
        adapter = SimpleNamespace(_latex_normalization_enabled=False)
        adapter.set_latex_normalization_enabled = lambda value: setattr(
            adapter, "_latex_normalization_enabled", bool(value)
        )
        runner.adapters = {Platform.FEISHU: adapter}

        result = await runner._handle_latex_command(_make_event(command))
        saved = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return result, saved, adapter

    def test_latex_on_persists_feishu_extra_and_updates_adapter(self, tmp_path, monkeypatch):
        result, saved, adapter = asyncio.run(
            self._run_latex_command(tmp_path, monkeypatch, "/latex on")
        )

        assert "ON" in result
        assert adapter._latex_normalization_enabled is True
        assert saved["platforms"]["feishu"]["extra"]["latex_normalization_enabled"] is True

    def test_latex_off_persists_feishu_extra_and_updates_adapter(self, tmp_path, monkeypatch):
        result, saved, adapter = asyncio.run(
            self._run_latex_command(tmp_path, monkeypatch, "/latex off")
        )

        assert "OFF" in result
        assert adapter._latex_normalization_enabled is False
        assert saved["platforms"]["feishu"]["extra"]["latex_normalization_enabled"] is False

    def test_latex_status_reports_current_adapter_state(self, tmp_path, monkeypatch):
        result, _saved, adapter = asyncio.run(
            self._run_latex_command(tmp_path, monkeypatch, "/latex status")
        )

        assert "OFF" in result
        assert adapter._latex_normalization_enabled is False

    def test_latex_rejects_non_feishu_platform(self, tmp_path, monkeypatch):
        hermes_home = tmp_path / "hermes"
        hermes_home.mkdir()
        monkeypatch.setattr(gateway_run, "_hermes_home", hermes_home)

        runner = _make_runner()
        result = asyncio.run(runner._handle_latex_command(_make_event("/latex on", platform=Platform.TELEGRAM)))

        assert "Feishu" in result
