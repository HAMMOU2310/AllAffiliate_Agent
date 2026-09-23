"""Tests for Logger and Settings v1.0 Batch 1 changes."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ── Logger Tests ─────────────────────────────────────────────────


class TestLoggerConstruction:
    def test_import_succeeds(self):
        from core.logger import Logger
        assert Logger is not None

    def test_has_required_methods(self):
        from core.logger import Logger
        assert callable(getattr(Logger, "info", None))
        assert callable(getattr(Logger, "success", None))
        assert callable(getattr(Logger, "warning", None))
        assert callable(getattr(Logger, "error", None))


class TestLoggerInitialization:
    def test_init_creates_logger(self):
        import core.logger as mod
        mod._INITIALIZED = False
        mod._init_root()
        logger = logging.getLogger("allaffiliate")
        assert logger is not None
        assert len(logger.handlers) > 0
        mod._INITIALIZED = False

    def test_init_idempotent(self):
        import core.logger as mod
        mod._INITIALIZED = False
        mod._init_root()
        count1 = len(logging.getLogger("allaffiliate").handlers)
        mod._init_root()
        count2 = len(logging.getLogger("allaffiliate").handlers)
        assert count1 == count2
        mod._INITIALIZED = False

    def test_init_with_env_level(self, monkeypatch):
        import core.logger as mod
        monkeypatch.setenv("APP_LOG_LEVEL", "DEBUG")
        mod._INITIALIZED = False
        mod._init_root()
        logger = logging.getLogger("allaffiliate")
        assert logger.level == logging.DEBUG
        mod._INITIALIZED = False
        monkeypatch.delenv("APP_LOG_LEVEL", raising=False)

    def test_init_default_level(self, monkeypatch):
        import core.logger as mod
        monkeypatch.delenv("APP_LOG_LEVEL", raising=False)
        mod._INITIALIZED = False
        mod._init_root()
        logger = logging.getLogger("allaffiliate")
        assert logger.level == logging.INFO
        mod._INITIALIZED = False


class TestLoggerLevels:
    def test_info_does_not_raise(self):
        from core.logger import Logger
        Logger.info("test info message")

    def test_success_does_not_raise(self):
        from core.logger import Logger
        Logger.success("test success message")

    def test_warning_does_not_raise(self):
        from core.logger import Logger
        Logger.warning("test warning message")

    def test_error_does_not_raise(self):
        from core.logger import Logger
        Logger.error("test error message")


class TestLoggerFileOutput:
    def test_file_created(self, tmp_path):
        import core.logger as mod
        with patch.object(mod, "_LOG_DIR", tmp_path):
            mod._init_root(force=True)
            from core.logger import Logger
            Logger.info("file creation test")
            log_file = tmp_path / "app.log"
            assert log_file.exists()
            mod._INITIALIZED = False

    def test_file_contains_message(self, tmp_path):
        import core.logger as mod
        with patch.object(mod, "_LOG_DIR", tmp_path):
            mod._init_root(force=True)
            from core.logger import Logger
            Logger.info("unique test marker 12345")
            log_file = tmp_path / "app.log"
            content = log_file.read_text(encoding="utf-8")
            assert "unique test marker 12345" in content
            mod._INITIALIZED = False

    def test_file_contains_timestamp(self, tmp_path):
        import core.logger as mod
        with patch.object(mod, "_LOG_DIR", tmp_path):
            mod._init_root(force=True)
            from core.logger import Logger
            Logger.info("timestamp test")
            log_file = tmp_path / "app.log"
            content = log_file.read_text(encoding="utf-8")
            assert "202" in content
            mod._INITIALIZED = False

    def test_file_contains_level(self, tmp_path):
        import core.logger as mod
        with patch.object(mod, "_LOG_DIR", tmp_path):
            mod._init_root(force=True)
            from core.logger import Logger
            Logger.warning("level test")
            log_file = tmp_path / "app.log"
            content = log_file.read_text(encoding="utf-8")
            assert "WARNING" in content
            mod._INITIALIZED = False

    def test_error_level_in_file(self, tmp_path):
        import core.logger as mod
        with patch.object(mod, "_LOG_DIR", tmp_path):
            mod._init_root(force=True)
            from core.logger import Logger
            Logger.error("error level test")
            log_file = tmp_path / "app.log"
            content = log_file.read_text(encoding="utf-8")
            assert "ERROR" in content
            mod._INITIALIZED = False


class TestLoggerRotation:
    def test_rotating_handler_configured(self):
        import core.logger as mod
        import logging.handlers
        mod._init_root(force=True)
        logger = logging.getLogger("allaffiliate")
        rotating = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(rotating) == 1
        assert rotating[0].maxBytes == 5 * 1024 * 1024
        assert rotating[0].backupCount == 3
        mod._INITIALIZED = False


class TestLoggerInvalidLevel:
    def test_invalid_level_defaults_to_info(self, monkeypatch):
        import core.logger as mod
        monkeypatch.setenv("APP_LOG_LEVEL", "NOT_A_LEVEL")
        mod._INITIALIZED = False
        mod._init_root()
        logger = logging.getLogger("allaffiliate")
        assert logger.level == logging.INFO
        mod._INITIALIZED = False
        monkeypatch.delenv("APP_LOG_LEVEL", raising=False)


class TestLoggerBackwardCompat:
    def test_console_output_still_works(self, capsys):
        from core.logger import Logger
        Logger.info("compat test")
        captured = capsys.readouterr()
        assert "compat test" in captured.out

    def test_warning_console_output(self, capsys):
        from core.logger import Logger
        Logger.warning("warn compat")
        captured = capsys.readouterr()
        assert "warn compat" in captured.out

    def test_error_console_output(self, capsys):
        from core.logger import Logger
        Logger.error("error compat")
        captured = capsys.readouterr()
        assert "error compat" in captured.out

    def test_success_console_output(self, capsys):
        from core.logger import Logger
        Logger.success("success compat")
        captured = capsys.readouterr()
        assert "success compat" in captured.out


# ── Settings Tests ───────────────────────────────────────────────


class TestSettingsConstruction:
    def test_loads_json(self):
        from core.settings import Settings
        s = Settings()
        assert s.get("project_name") == "AllAffiliate_Agent"

    def test_has_required_methods(self):
        from core.settings import Settings
        s = Settings()
        assert callable(getattr(s, "get", None))
        assert callable(getattr(s, "set", None))
        assert callable(getattr(s, "save", None))
        assert callable(getattr(s, "load", None))


class TestSettingsDefaults:
    def test_default_workspace(self):
        from core.settings import Settings
        s = Settings()
        assert s.get("workspace") == "workspace"

    def test_default_output_folder(self):
        from core.settings import Settings
        s = Settings()
        assert s.get("output_folder") == "outputs"

    def test_default_language(self):
        from core.settings import Settings
        s = Settings()
        assert s.get("language") == "ar"

    def test_missing_key_returns_none(self):
        from core.settings import Settings
        s = Settings()
        assert s.get("nonexistent_key") is None

    def test_missing_key_returns_default(self):
        from core.settings import Settings
        s = Settings()
        assert s.get("nonexistent_key", "fallback") == "fallback"


class TestSettingsEnvOverrides:
    def test_app_log_level_overrides(self, monkeypatch):
        monkeypatch.setenv("APP_LOG_LEVEL", "DEBUG")
        from core.settings import Settings
        s = Settings()
        assert s.get("log_level") == "DEBUG"
        monkeypatch.delenv("APP_LOG_LEVEL", raising=False)

    def test_app_workspace_overrides(self, monkeypatch):
        monkeypatch.setenv("APP_WORKSPACE", "custom_workspace")
        from core.settings import Settings
        s = Settings()
        assert s.get("workspace") == "custom_workspace"
        monkeypatch.delenv("APP_WORKSPACE", raising=False)

    def test_app_output_folder_overrides(self, monkeypatch):
        monkeypatch.setenv("APP_OUTPUT_FOLDER", "custom_outputs")
        from core.settings import Settings
        s = Settings()
        assert s.get("output_folder") == "custom_outputs"
        monkeypatch.delenv("APP_OUTPUT_FOLDER", raising=False)

    def test_empty_env_does_not_erase(self, monkeypatch):
        monkeypatch.setenv("APP_WORKSPACE", "")
        from core.settings import Settings
        s = Settings()
        assert s.get("workspace") == "workspace"
        monkeypatch.delenv("APP_WORKSPACE", raising=False)

    def test_whitespace_only_env_does_not_erase(self, monkeypatch):
        monkeypatch.setenv("APP_WORKSPACE", "   ")
        from core.settings import Settings
        s = Settings()
        assert s.get("workspace") == "workspace"
        monkeypatch.delenv("APP_WORKSPACE", raising=False)

    def test_missing_env_preserves_json(self, monkeypatch):
        monkeypatch.delenv("APP_LOG_LEVEL", raising=False)
        monkeypatch.delenv("APP_WORKSPACE", raising=False)
        monkeypatch.delenv("APP_OUTPUT_FOLDER", raising=False)
        from core.settings import Settings
        s = Settings()
        assert s.get("workspace") == "workspace"
        assert s.get("output_folder") == "outputs"


class TestSettingsSetAndSave:
    def test_set_in_memory(self):
        from core.settings import Settings
        s = Settings()
        s.set("test_key", "test_value")
        assert s.get("test_key") == "test_value"

    def test_save_persists(self, tmp_path):
        import json
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        settings_file = config_dir / "settings.json"
        settings_file.write_text(json.dumps({"workspace": "workspace"}), encoding="utf-8")
        from core.settings import Settings
        s = Settings()
        s._file = settings_file
        s.set("workspace", "new_workspace")
        s.save()
        reloaded = json.loads(settings_file.read_text(encoding="utf-8"))
        assert reloaded["workspace"] == "new_workspace"
