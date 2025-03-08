from libtmux import Server
from tmuxp.workspace.builder import WorkspaceBuilder
import os
from .workspace import detect_workspace, has_dev_script, detect_package_manager


def build_session_config(directory):
    editor = os.environ.get("EDITOR", "vim")
    session_name = os.path.basename(directory)
    package_dirs = detect_workspace(directory)

    if package_dirs:
        windows = []

        for package_dir in package_dirs:
            package_name = os.path.basename(package_dir)
            has_dev = has_dev_script(package_dir)
            pkg_manager = detect_package_manager(package_dir)

            panes = [
                {"shell_command": [{"cmd": editor}]},
                {"shell_command": []},  # Empty shell pane
            ]

            if has_dev:
                if pkg_manager == "npm":
                    panes.insert(1, {"shell_command": [{"cmd": "npm run dev"}]})
                else:
                    panes.insert(1, {"shell_command": [{"cmd": f"{pkg_manager} dev"}]})

            windows.append(
                {
                    "window_name": package_name,
                    "layout": "main-vertical",
                    "start_directory": package_dir,
                    "options": {"main-pane-width": "50%"},
                    "panes": panes,
                }
            )

        return {
            "session_name": session_name,
            "windows": windows,
        }
    else:
        venv_activate_path = os.path.join(directory, "venv", "bin", "activate")
        has_venv = os.path.isfile(venv_activate_path)

        editor_commands = []
        if has_venv:
            editor_commands.append({"cmd": f"source {venv_activate_path}"})

        editor_commands.append({"cmd": editor})

        return {
            "session_name": session_name,
            "windows": [
                {
                    # No window_name specified, so it will show the running process
                    "layout": "main-vertical",
                    "start_directory": directory,
                    "options": {"main-pane-width": "50%"},
                    "panes": [
                        {"shell_command": editor_commands},
                        {
                            "shell_command": has_venv
                            and [{"cmd": f"source {venv_activate_path}"}]
                            or []
                        },
                    ],
                }
            ],
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
