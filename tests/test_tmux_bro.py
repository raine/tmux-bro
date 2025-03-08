import json
import os

import pytest
import toml
import yaml

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
