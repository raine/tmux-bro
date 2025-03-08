import yaml
from unittest.mock import patch
from tmux_bro.config import load_global_config


def test_load_global_config_file_not_exists():
    """Test loading config when file doesn't exist"""
    with patch("tmux_bro.config.get_global_config_path") as mock_path:
        mock_path.return_value = "/nonexistent/path/to/config.yaml"
        config = load_global_config()
        assert config == {}


def test_load_global_config_empty_file(tmp_path):
    """Test loading config from an empty file"""
    config_file = tmp_path / "tmux-bro.yaml"
    config_file.touch()  # Creates an empty file

    with patch("tmux_bro.config.get_global_config_path") as mock_path:
        mock_path.return_value = str(config_file)
        config = load_global_config()
        assert config == {}


def test_load_global_config_valid_yaml(tmp_path):
    """Test loading config from a valid YAML file"""
    test_config = {"default_layout": "main-vertical"}

    # Create a config file with valid YAML content
    config_file = tmp_path / "tmux-bro.yaml"
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)

    with patch("tmux_bro.config.get_global_config_path") as mock_path:
        mock_path.return_value = str(config_file)
        config = load_global_config()
        assert config == test_config
