import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "project_path": "",
    "res_path": "",
    "dpi_presets": {
        "mdpi": "0.25",
        "hdpi": "0.375",
        "xhdpi": "0.5",
        "xxhdpi": "0.75",
        "xxxhdpi": "1.0"
    },
    "dpi_enabled": {
        "mdpi": True,
        "hdpi": True,
        "xhdpi": True,
        "xxhdpi": True,
        "xxxhdpi": True
    },
    "webp": False
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()

    # Мержим с дефолтом, чтобы при обновлении всё работало
    config = DEFAULT_CONFIG.copy()
    config.update(data)
    config["dpi_presets"].update(data.get("dpi_presets", {}))
    config["dpi_enabled"].update(data.get("dpi_enabled", {}))
    return config


def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении config.json: {e}")
