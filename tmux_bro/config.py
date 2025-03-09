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


def load_project_config(directory: str) -> Dict[str, Any]:
    """
    Load project-specific configuration from .tmux-bro.yaml in the repository root.
    First tries to find the Git root directory, then falls back to the provided directory.
    Returns a dictionary with configuration values or empty dict if no config exists.
    """
    from .git import get_git_root

    git_root = get_git_root(directory)
    config_paths = []

    if git_root:
        config_paths.append(os.path.join(git_root, ".tmux-bro.yaml"))

    if not git_root or os.path.normpath(git_root) != os.path.normpath(directory):
        config_paths.append(os.path.join(directory, ".tmux-bro.yaml"))

    for config_path in config_paths:
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                return config or {}
            except Exception as e:
                print(f"Warning: Error loading project config file {config_path}: {e}")

    return {}

