import json
from pathlib import Path
from typing import List

CONFIG_FILE = Path.home() / ".config" / "vibe-streamer" / "config.json"


class Config:
    def __init__(self):
        self.root_dirs: List[str] = []
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.root_dirs = data.get("root_dirs", [])
            except Exception as e:
                print(f"Error loading config: {e}")
                self.root_dirs = []
        else:
            self.root_dirs = []

    def save(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"root_dirs": self.root_dirs}, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_root_dir(self, path: str):
        if path not in self.root_dirs:
            self.root_dirs.append(path)
            self.save()

    def remove_root_dir(self, path: str):
        if path in self.root_dirs:
            self.root_dirs.remove(path)
            self.save()


config = Config()
