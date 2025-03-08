import os
import yaml
from typing import Dict, Any


def get_global_config_path() -> str:
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".config", "tmux-bro.yaml")


def load_global_config() -> Dict[str, Any]:
    """
    Load global user configuration from ~/.config/tmux-bro.yaml
    Returns a dictionary with configuration values or empty dict if no config exists.
    """
    config_path = get_global_config_path()

    if not os.path.isfile(config_path):
        return {}

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config or {}
    except Exception as e:
        print(f"Warning: Error loading global config file {config_path}: {e}")
        return {}
