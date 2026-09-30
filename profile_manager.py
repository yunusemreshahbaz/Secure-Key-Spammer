import json
import os

class ProfileManager:
    def __init__(self, filename="profiles.json"):
        self.filename = filename
        self.profiles = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, indent=4, ensure_ascii=False)

    def add_or_update(self, name, data):
        self.profiles[name] = data
        self.save()

    def get_profile(self, name):
        return self.profiles.get(name, {})

    def get_all_names(self):
        return list(self.profiles.keys())