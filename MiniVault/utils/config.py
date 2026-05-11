import configparser
from pathlib import Path

CONFIG_PATH = Path("data/config.ini")

def load_config() -> dict:
    config = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        config.read(CONFIG_PATH)
        return dict(config["DEFAULT"])
    return {}

def save_config(data: dict):
    config = configparser.ConfigParser()
    config["DEFAULT"] = data
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        config.write(f)