"""Application settings with JSON defaults and environment overrides.

Environment variables override JSON values when explicitly set:
    APP_LOG_LEVEL    -> log level (DEBUG/INFO/WARNING/ERROR)
    APP_WORKSPACE    -> workspace directory
    APP_OUTPUT_FOLDER -> output directory

Empty/missing env vars do NOT erase valid JSON defaults.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


_ENV_OVERRIDES = {
    "APP_LOG_LEVEL": "log_level",
    "APP_WORKSPACE": "workspace",
    "APP_OUTPUT_FOLDER": "output_folder",
}


class Settings:

    def __init__(self):

        self._file = Path(__file__).resolve().parent.parent / "config" / "settings.json"

        self._data = {}

        self.load()

    def load(self):

        with open(self._file, "r", encoding="utf-8") as file:

            self._data = json.load(file)

        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        for env_key, setting_key in _ENV_OVERRIDES.items():
            env_val = os.getenv(env_key)
            if env_val is not None and env_val.strip():
                self._data[setting_key] = env_val.strip()

    def get(self, key, default=None):

        return self._data.get(key, default)

    def set(self, key, value):

        self._data[key] = value

    def save(self):

        with open(self._file, "w", encoding="utf-8") as file:

            json.dump(self._data, file, indent=4, ensure_ascii=False)
