from libtmux import Server
from tmuxp.workspace.builder import WorkspaceBuilder
import os
from .workspace import (
    detect_workspace,
    has_package_json_dev_script,
    detect_package_manager,
)
from .config import load_global_config, load_project_config


def _get_venv_source_cmd(directory):
    """Return venv source command if a venv exists in the directory."""
    venv_activate_path = os.path.join(directory, "venv", "bin", "activate")
    if os.path.isfile(venv_activate_path):
        return {"cmd": f"source {venv_activate_path}"}
    return None


def _create_editor_pane(directory, editor):
    """Create editor pane with venv activation if needed."""
    commands = []
    venv_cmd = _get_venv_source_cmd(directory)
    if venv_cmd:
        commands.append(venv_cmd)
    commands.append({"cmd": editor})
    return {"shell_command": commands}


def _create_shell_pane(directory):
    """Create shell pane with venv activation if needed."""
    commands = []
    venv_cmd = _get_venv_source_cmd(directory)
    if venv_cmd:
        commands.append(venv_cmd)
    return {"shell_command": commands}


def _create_dev_pane(directory, pkg_manager, dev_command=None):
    """Create dev script pane with appropriate command."""
    commands = []
    venv_cmd = _get_venv_source_cmd(directory)
    if venv_cmd:
        commands.append(venv_cmd)

    if dev_command:
        commands.append({"cmd": dev_command})
    elif pkg_manager == "npm":
        commands.append({"cmd": "npm run dev"})
    else:
        commands.append({"cmd": f"{pkg_manager} dev"})

    return {"shell_command": commands}


DEFAULT_LAYOUT = "main-vertical"
DEFAULT_MAIN_PANE_WIDTH = "50%"
DEFAULT_MAIN_PANE_HEIGHT = "50%"


def _create_window_config(directory, window_name=None):
    """Create a standard window configuration."""
    global_config = load_global_config()
    project_config = load_project_config(directory)

    # Get layout and pane dimensions from project config, global config, or use defaults
    layout = project_config.get("layout", global_config.get("layout", DEFAULT_LAYOUT))
    main_pane_width = project_config.get(
        "main_pane_width", global_config.get("main_pane_width", DEFAULT_MAIN_PANE_WIDTH)
    )
    main_pane_height = project_config.get(
        "main_pane_height",
        global_config.get("main_pane_height", DEFAULT_MAIN_PANE_HEIGHT),
    )

    # Set options based on layout type
    options = {}
    if layout in ["main-vertical", "even-vertical"]:
        options["main-pane-width"] = main_pane_width
    elif layout in ["main-horizontal", "even-horizontal"]:
        options["main-pane-height"] = main_pane_height
    else:  # For tiled and other layouts
        options["main-pane-width"] = main_pane_width
        options["main-pane-height"] = main_pane_height

    config = {
        "layout": layout,
        "start_directory": directory,
        "options": options,
        "suppress_history": False,
    }

    if window_name is not None:
        config["window_name"] = window_name

    return config


def build_session_config(directory):
    editor = os.environ.get("EDITOR", "vim")
    session_name = os.path.basename(directory)
    package_dirs = detect_workspace(directory)
    pkg_manager = detect_package_manager(directory)

    project_config = load_project_config(directory)
    default_dev_command = project_config.get("dev_command")
    package_configs = project_config.get("packages", {})

    windows = []

    if package_dirs:
        # Multi-package workspace
        for package_dir in package_dirs:
            package_name = os.path.basename(package_dir)

            # Check for package-specific dev command override
            package_dev_command = None
            if (
                package_name in package_configs
                and "dev_command" in package_configs[package_name]
            ):
                package_dev_command = package_configs[package_name]["dev_command"]
            else:
                package_dev_command = default_dev_command

            # Add dev pane if package has dev script or if dev command is specified in config
            has_dev = (
                has_package_json_dev_script(package_dir)
                or package_dev_command is not None
            )

            panes = [
                _create_editor_pane(package_dir, editor),
                _create_shell_pane(package_dir),
            ]

            if has_dev:
                panes.insert(
                    1, _create_dev_pane(package_dir, pkg_manager, package_dev_command)
                )

            window = _create_window_config(package_dir, package_name)
            window["panes"] = panes
            windows.append(window)
    else:
        # Single directory
        has_dev = (
            has_package_json_dev_script(directory) or default_dev_command is not None
        )

        panes = [
            _create_editor_pane(directory, editor),
            _create_shell_pane(directory),
        ]

        if has_dev:
            panes.insert(
                1, _create_dev_pane(directory, pkg_manager, default_dev_command)
            )

        window = _create_window_config(directory)
        window["panes"] = panes
        windows.append(window)

    return {
        "session_name": session_name,
        "windows": windows,
    }


def create_tmux_session(config):
    server = Server()

    builder = WorkspaceBuilder(session_config=config, server=server)
    builder.build()
    session = builder.session

    if "TMUX" in os.environ:
        # If we're already in a tmux session, switch client
        tmux_env = os.environ.pop("TMUX")
        session.switch_client()
        os.environ["TMUX"] = tmux_env
    else:
        # Otherwise attach to the new session
        session.attach_session()

    return session


def find_tmux_session(session_name):
    """Find an existing tmux session by name."""
    server = Server()
    return server.find_where({"session_name": session_name})
