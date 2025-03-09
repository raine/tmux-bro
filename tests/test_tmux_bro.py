import json
import os

import pytest
import toml
import yaml
from unittest.mock import patch

from tmux_bro.tmux import build_session_config


@pytest.fixture(autouse=True)
def editor_env():
    """Set up the EDITOR environment variable for testing."""
    old_editor = os.environ.get("EDITOR")
    os.environ["EDITOR"] = "vim"
    yield
    if old_editor:
        os.environ["EDITOR"] = old_editor
    else:
        del os.environ["EDITOR"]


@pytest.fixture(autouse=True)
def mock_global_config():
    """Mock the global config to prevent real config from affecting tests."""
    with patch("tmux_bro.tmux.load_global_config") as mock_config:
        # Default to empty config
        mock_config.return_value = {}
        yield mock_config


@pytest.fixture
def simple_dir(tmp_path):
    """Create a simple project directory."""
    project_dir = tmp_path / "simple-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def python_venv_dir(tmp_path):
    """Create a Python project with virtual environment."""
    project_dir = tmp_path / "python-project"
    project_dir.mkdir()

    # Create venv structure
    venv_dir = project_dir / "venv" / "bin"
    venv_dir.mkdir(parents=True)
    activate_file = venv_dir / "activate"
    activate_file.write_text("# Mock activate script")

    return project_dir


@pytest.fixture
def npm_workspace_dir(tmp_path):
    """Create a fixture npm workspace directory."""
    workspace_dir = tmp_path / "npm-workspace"
    workspace_dir.mkdir()

    # Create root package.json
    package_json = workspace_dir / "package.json"
    package_json.write_text(
        json.dumps({"name": "workspace-root", "workspaces": ["packages/*"]})
    )

    # Create package-lock.json
    lock_file = workspace_dir / "package-lock.json"
    lock_file.write_text("{}")

    # Create packages directory with two packages
    packages_dir = workspace_dir / "packages"
    packages_dir.mkdir()

    # Package 1 with dev script
    pkg1_dir = packages_dir / "pkg1"
    pkg1_dir.mkdir()
    pkg1_json = pkg1_dir / "package.json"
    pkg1_json.write_text(json.dumps({"name": "pkg1", "scripts": {"dev": "vite"}}))

    # Package 2 without dev script
    pkg2_dir = packages_dir / "pkg2"
    pkg2_dir.mkdir()
    pkg2_json = pkg2_dir / "package.json"
    pkg2_json.write_text(json.dumps({"name": "pkg2"}))

    return workspace_dir


@pytest.fixture
def pnpm_workspace_dir(tmp_path):
    """Create a fixture pnpm workspace directory."""
    workspace_dir = tmp_path / "pnpm-workspace"
    workspace_dir.mkdir()
    # Create workspace yaml
    workspace_yaml = workspace_dir / "pnpm-workspace.yaml"
    workspace_yaml.write_text(yaml.dump({"packages": ["packages/*"]}))

    # Create pnpm-lock.yaml
    lock_file = workspace_dir / "pnpm-lock.yaml"
    lock_file.write_text("{}")

    # Create packages directory with two packages
    packages_dir = workspace_dir / "packages"
    packages_dir.mkdir()

    # Package 1 with dev script
    pkg1_dir = packages_dir / "pkg1"
    pkg1_dir.mkdir()
    pkg1_json = pkg1_dir / "package.json"
    pkg1_json.write_text(json.dumps({"name": "pkg1", "scripts": {"dev": "vite"}}))

    # Package 2 without dev script
    pkg2_dir = packages_dir / "pkg2"
    pkg2_dir.mkdir()
    pkg2_json = pkg2_dir / "package.json"
    pkg2_json.write_text(json.dumps({"name": "pkg2"}))

    return workspace_dir


@pytest.fixture
def cargo_workspace_dir(tmp_path):
    """Create a fixture Cargo workspace directory."""
    workspace_dir = tmp_path / "cargo-workspace"
    workspace_dir.mkdir()

    # Create root Cargo.toml
    cargo_toml = workspace_dir / "Cargo.toml"
    cargo_toml.write_text(toml.dumps({"workspace": {"members": ["crate1", "crate2"]}}))

    # Create Cargo.lock
    lock_file = workspace_dir / "Cargo.lock"
    lock_file.write_text("")

    # Create crates
    crate1_dir = workspace_dir / "crate1"
    crate1_dir.mkdir()
    crate1_toml = crate1_dir / "Cargo.toml"
    crate1_toml.write_text(
        toml.dumps({"package": {"name": "crate1", "version": "0.1.0"}})
    )

    crate2_dir = workspace_dir / "crate2"
    crate2_dir.mkdir()
    crate2_toml = crate2_dir / "Cargo.toml"
    crate2_toml.write_text(
        toml.dumps({"package": {"name": "crate2", "version": "0.1.0"}})
    )

    return workspace_dir


@pytest.fixture
def npm_project_dir(tmp_path):
    """Create a fixture for a single npm project with dev script."""
    project_dir = tmp_path / "npm-project"
    project_dir.mkdir()

    # Create package.json with dev script
    package_json = project_dir / "package.json"
    package_json.write_text(
        json.dumps(
            {"name": "npm-project", "version": "1.0.0", "scripts": {"dev": "vite"}}
        )
    )

    # Create package-lock.json
    lock_file = project_dir / "package-lock.json"
    lock_file.write_text("{}")

    return project_dir


@pytest.fixture
def npm_project_dir_no_dev_script(tmp_path):
    """Create a fixture for a single npm project with dev script."""
    project_dir = tmp_path / "npm-project"
    project_dir.mkdir()

    # Create package.json with dev script
    package_json = project_dir / "package.json"
    package_json.write_text(json.dumps({"name": "npm-project", "version": "1.0.0"}))

    # Create package-lock.json
    lock_file = project_dir / "package-lock.json"
    lock_file.write_text("{}")

    return project_dir


@pytest.fixture
def npm_project_with_dev_override(tmp_path):
    """Create a fixture for a single npm project with a dev script and a .tmux-bro.yaml config."""
    project_dir = tmp_path / "npm-project-custom"
    project_dir.mkdir()

    # Create package.json with dev script
    package_json = project_dir / "package.json"
    package_json.write_text(
        '{"name": "npm-project-custom", "version": "1.0.0", "scripts": {"dev": "vite"}}'
    )

    # Create package-lock.json
    lock_file = project_dir / "package-lock.json"
    lock_file.write_text("{}")

    # Create .tmux-bro.yaml with dev command override
    config_file = project_dir / ".tmux-bro.yaml"
    config_file.write_text(yaml.dump({"dev_command": "hello world"}))

    return project_dir


@pytest.fixture
def npm_workspace_with_overrides(tmp_path):
    """Create a fixture npm workspace with custom dev commands."""
    workspace_dir = tmp_path / "npm-workspace-custom"
    workspace_dir.mkdir()

    # Create root package.json
    package_json = workspace_dir / "package.json"
    package_json.write_text(
        '{"name": "workspace-root-custom", "workspaces": ["packages/*"]}'
    )

    # Create package-lock.json
    lock_file = workspace_dir / "package-lock.json"
    lock_file.write_text("{}")

    # Create packages directory with two packages
    packages_dir = workspace_dir / "packages"
    packages_dir.mkdir()

    # Package 1 with dev script
    pkg1_dir = packages_dir / "pkg1"
    pkg1_dir.mkdir()
    pkg1_json = pkg1_dir / "package.json"
    pkg1_json.write_text('{"name": "pkg1", "scripts": {"dev": "vite"}}')

    # Package 2 without dev script
    pkg2_dir = packages_dir / "pkg2"
    pkg2_dir.mkdir()
    pkg2_json = pkg2_dir / "package.json"
    pkg2_json.write_text('{"name": "pkg2", "scripts": {"dev": "vite"}}')

    # Create .tmux-bro.yaml with dev command overrides
    config_file = workspace_dir / ".tmux-bro.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "dev_command": "npm run start:dev",
                "packages": {"pkg1": {"dev_command": "npm run custom-dev:pkg1"}},
            }
        )
    )

    return workspace_dir


@pytest.fixture
def npm_project_no_dev_script_with_override(tmp_path):
    """Create a fixture for a single npm project without dev script but with dev_command in config."""
    project_dir = tmp_path / "npm-project-no-dev"
    project_dir.mkdir()

    # Create package.json without dev script
    package_json = project_dir / "package.json"
    package_json.write_text(
        json.dumps({"name": "npm-project-no-dev", "version": "1.0.0"})
    )

    # Create package-lock.json
    lock_file = project_dir / "package-lock.json"
    lock_file.write_text("{}")

    # Create .tmux-bro.yaml with dev command override
    config_file = project_dir / ".tmux-bro.yaml"
    config_file.write_text(yaml.dump({"dev_command": "hello world"}))

    return project_dir


def test_simple_directory(simple_dir):
    """Test configuration for a simple directory without workspace."""
    config = build_session_config(str(simple_dir))
    expected = {
        "session_name": "simple-project",
        "windows": [
            {
                "layout": "main-vertical",
                "start_directory": str(simple_dir),
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": []},
                ],
            }
        ],
    }

    assert expected == config


def test_python_venv_directory(python_venv_dir):
    """Test configuration for a Python project with venv."""
    config = build_session_config(str(python_venv_dir))

    venv_path = str(python_venv_dir / "venv" / "bin" / "activate")
    expected = {
        "session_name": "python-project",
        "windows": [
            {
                "layout": "main-vertical",
                "start_directory": str(python_venv_dir),
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": f"source {venv_path}"}, {"cmd": "vim"}]},
                    {"shell_command": [{"cmd": f"source {venv_path}"}]},
                ],
            }
        ],
    }

    assert expected == config


def test_npm_workspace(npm_workspace_dir):
    """Test configuration for an npm workspace."""
    config = build_session_config(str(npm_workspace_dir))

    pkg1_path = str(npm_workspace_dir / "packages" / "pkg1")
    pkg2_path = str(npm_workspace_dir / "packages" / "pkg2")

    expected = {
        "session_name": "npm-workspace",
        "windows": [
            {
                "window_name": "pkg2",
                "layout": "main-vertical",
                "start_directory": pkg2_path,
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": []},
                ],
            },
            {
                "window_name": "pkg1",
                "layout": "main-vertical",
                "start_directory": pkg1_path,
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": [{"cmd": "npm run dev"}]},
                    {"shell_command": []},
                ],
            },
        ],
    }

    assert expected == config


def test_pnpm_workspace(pnpm_workspace_dir):
    """Test configuration for a pnpm workspace."""
    config = build_session_config(str(pnpm_workspace_dir))

    pkg1_path = str(pnpm_workspace_dir / "packages" / "pkg1")
    pkg2_path = str(pnpm_workspace_dir / "packages" / "pkg2")

    expected = {
        "session_name": "pnpm-workspace",
        "windows": [
            {
                "window_name": "pkg2",
                "layout": "main-vertical",
                "start_directory": pkg2_path,
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": []},
                ],
            },
            {
                "window_name": "pkg1",
                "layout": "main-vertical",
                "start_directory": pkg1_path,
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": [{"cmd": "pnpm dev"}]},
                    {"shell_command": []},
                ],
            },
        ],
    }

    assert expected == config


def test_cargo_workspace(cargo_workspace_dir):
    """Test configuration for a Cargo workspace."""
    config = build_session_config(str(cargo_workspace_dir))

    crate1_path = str(cargo_workspace_dir / "crate1")
    crate2_path = str(cargo_workspace_dir / "crate2")

    expected = {
        "session_name": "cargo-workspace",
        "windows": [
            {
                "window_name": "crate1",
                "layout": "main-vertical",
                "start_directory": crate1_path,
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": []},
                ],
            },
            {
                "window_name": "crate2",
                "layout": "main-vertical",
                "start_directory": crate2_path,
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": []},
                ],
            },
        ],
    }

    assert expected == config


def test_npm_project(npm_project_dir):
    """Test configuration for a single npm project with dev script."""
    config = build_session_config(str(npm_project_dir))

    expected = {
        "session_name": "npm-project",
        "windows": [
            {
                "layout": "main-vertical",
                "start_directory": str(npm_project_dir),
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": [{"cmd": "npm run dev"}]},
                    {"shell_command": []},
                ],
            }
        ],
    }

    assert expected == config


def test_npm_project_no_dev_script(npm_project_dir_no_dev_script):
    """Test configuration for a single npm project with dev script."""
    config = build_session_config(str(npm_project_dir_no_dev_script))

    expected = {
        "session_name": "npm-project",
        "windows": [
            {
                "layout": "main-vertical",
                "start_directory": str(npm_project_dir_no_dev_script),
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": []},
                ],
            }
        ],
    }

    assert expected == config


def test_npm_project_no_dev_script_with_override(
    npm_project_no_dev_script_with_override,
):
    """Test configuration for a single npm project without dev script but with dev_command in config."""
    with patch("tmux_bro.git.get_git_root", return_value=None):
        config = build_session_config(str(npm_project_no_dev_script_with_override))

    expected = {
        "session_name": "npm-project-no-dev",
        "windows": [
            {
                "layout": "main-vertical",
                "start_directory": str(npm_project_no_dev_script_with_override),
                "options": {"main-pane-width": "50%"},
                "panes": [
                    {"shell_command": [{"cmd": "vim"}]},
                    {"shell_command": [{"cmd": "hello world"}]},
                    {"shell_command": []},
                ],
            }
        ],
    }

    assert expected == config


def test_custom_layout_from_config(simple_dir, mock_global_config):
    """Test that layout is read from global config if it exists."""
    # Set the mock to return a custom layout
    mock_global_config.return_value = {"layout": "tiled"}
    config = build_session_config(str(simple_dir))

    # Check that the layout from config is used
    assert config["windows"][0]["layout"] == "tiled"


def test_default_layout_when_no_config(simple_dir):
    """Test that default layout is used when no layout in config."""
    config = build_session_config(str(simple_dir))

    # Check that the default layout is used
    assert config["windows"][0]["layout"] == "main-vertical"


def test_custom_pane_dimensions(simple_dir, mock_global_config):
    """Test that pane dimensions are read from global config."""
    # Set the mock to return custom pane dimensions
    mock_global_config.return_value = {
        "layout": "main-vertical",
        "main_pane_width": "70%",
    }

    config = build_session_config(str(simple_dir))

    # Check that the custom dimensions are used
    assert config["windows"][0]["options"]["main-pane-width"] == "70%"


def test_horizontal_layout_uses_pane_height(simple_dir, mock_global_config):
    """Test that horizontal layouts use main-pane-height."""
    # Set the mock to return a horizontal layout
    mock_global_config.return_value = {
        "layout": "main-horizontal",
        "main_pane_height": "75%",
    }

    config = build_session_config(str(simple_dir))

    # Check that main-pane-height is used for horizontal layout
    assert config["windows"][0]["layout"] == "main-horizontal"
    assert config["windows"][0]["options"]["main-pane-height"] == "75%"
    assert "main-pane-width" not in config["windows"][0]["options"]


def test_project_specific_dev_command(npm_project_with_dev_override):
    """Test that project-specific dev command override is applied."""
    with patch("tmux_bro.git.get_git_root", return_value=None):
        config = build_session_config(str(npm_project_with_dev_override))

    expected_dev_cmd = "hello world"
    actual_dev_cmd = config["windows"][0]["panes"][1]["shell_command"][0]["cmd"]

    assert actual_dev_cmd == expected_dev_cmd


def test_workspace_specific_dev_commands(npm_workspace_with_overrides):
    """Test that workspace-specific dev command overrides are applied correctly."""
    with patch("tmux_bro.git.get_git_root", return_value=None):
        config = build_session_config(str(npm_workspace_with_overrides))

    # Verify pkg1 uses its specific override
    pkg1_window = next(
        (w for w in config["windows"] if w["window_name"] == "pkg1"), None
    )
    assert pkg1_window is not None
    pkg1_dev_cmd = pkg1_window["panes"][1]["shell_command"][0]["cmd"]
    assert pkg1_dev_cmd == "npm run custom-dev:pkg1"

    # Verify pkg2 uses the default override
    pkg2_window = next(
        (w for w in config["windows"] if w["window_name"] == "pkg2"), None
    )
    assert pkg2_window is not None
    pkg2_dev_cmd = pkg2_window["panes"][1]["shell_command"][0]["cmd"]
    assert pkg2_dev_cmd == "npm run start:dev"
