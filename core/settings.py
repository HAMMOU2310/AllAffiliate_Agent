import json
from pathlib import Path


class Settings:

    def __init__(self):

        self._file = Path("config/settings.json")

        self._data = {}

        self.load()

    def load(self):

        with open(self._file, "r", encoding="utf-8") as file:

            self._data = json.load(file)

    def get(self, key, default=None):

        return self._data.get(key, default)

    def set(self, key, value):

        self._data[key] = value

    def save(self):

        with open(self._file, "w", encoding="utf-8") as file:

            json.dump(self._data, file, indent=4, ensure_ascii=False)