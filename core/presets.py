import json
import os

def load_presets(preset_dir="presets"):
    presets = {}
    for filename in os.listdir(preset_dir):
        if filename.endswith(".json"):
            path = os.path.join(preset_dir, filename)
            with open(path, "r") as f:
                try:
                    data = json.load(f)
                    presets[data["name"]] = data
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
    return presets
