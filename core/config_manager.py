import json
import os
import sys

# Определяем, куда класть конфиг
def get_config_dir():
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/PNG2Drawable")
    elif sys.platform == "win32":
        return os.path.join(os.getenv("APPDATA"), "PNG2Drawable")
    else:
        return os.path.expanduser("~/.png2drawable")


CONFIG_DIR = get_config_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

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
    except Exception as e:
        print(f"[Config] Ошибка при загрузке конфига: {e}")
        return DEFAULT_CONFIG.copy()

    config = DEFAULT_CONFIG.copy()
    config.update(data)
    config["dpi_presets"].update(data.get("dpi_presets", {}))
    config["dpi_enabled"].update(data.get("dpi_enabled", {}))
    return config


def save_config(config: dict):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Config] Ошибка при сохранении config.json: {e}")
