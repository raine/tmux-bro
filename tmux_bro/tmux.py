from libtmux import Server
from tmuxp.workspace.builder import WorkspaceBuilder
import os
from .workspace import detect_workspace, has_dev_script, detect_package_manager


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


def _create_dev_pane(directory, pkg_manager):
    """Create dev script pane with appropriate command."""
    commands = []
    venv_cmd = _get_venv_source_cmd(directory)
    if venv_cmd:
        commands.append(venv_cmd)

    if pkg_manager == "npm":
        commands.append({"cmd": "npm run dev"})
    else:
        commands.append({"cmd": f"{pkg_manager} dev"})

    return {"shell_command": commands}


def _create_window_config(directory, window_name=None):
    """Create a standard window configuration."""
    config = {
        "layout": "main-vertical",
        "start_directory": directory,
        "options": {"main-pane-width": "50%"},
    }

    if window_name is not None:
        config["window_name"] = window_name

    return config


def build_session_config(directory):
    editor = os.environ.get("EDITOR", "vim")
    session_name = os.path.basename(directory)
    package_dirs = detect_workspace(directory)
    pkg_manager = detect_package_manager(directory)

    windows = []

    if package_dirs:
        # Multi-package workspace
        for package_dir in package_dirs:
            package_name = os.path.basename(package_dir)
            has_dev = has_dev_script(package_dir)

            panes = [
                _create_editor_pane(package_dir, editor),
                _create_shell_pane(package_dir),
            ]

            if has_dev:
                panes.insert(1, _create_dev_pane(package_dir, pkg_manager))

            window = _create_window_config(package_dir, package_name)
            window["panes"] = panes
            windows.append(window)
    else:
        # Single directory
        has_dev = has_dev_script(directory)

        panes = [
            _create_editor_pane(directory, editor),
            _create_shell_pane(directory),
        ]

        if has_dev:
            panes.insert(1, _create_dev_pane(directory, pkg_manager))

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
