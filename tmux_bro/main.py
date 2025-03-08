import sys
import os
from . import tmux
from .fuzzy import run_fuzzy_finder


def main():
    selected_dir = run_fuzzy_finder()

    if selected_dir and isinstance(selected_dir, str):
        session_name = os.path.basename(selected_dir)
        existing_session = tmux.find_tmux_session(session_name)

        if existing_session:
            session = existing_session
        else:
            session_config = tmux.build_session_config(selected_dir)
            session = tmux.create_tmux_session(session_config)

        if "TMUX" in os.environ:
            # If we're already in a tmux session, switch client
            tmux_env = os.environ.pop("TMUX")
            session.switch_client()
            os.environ["TMUX"] = tmux_env
        else:
            # Otherwise attach to the new session
            session.attach_session()
    else:
        print("No directory was selected", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
