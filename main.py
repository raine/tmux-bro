import sys
import tmux
from fuzzy import run_fuzzy_finder


if __name__ == "__main__":
    selected_dir, key_pressed = run_fuzzy_finder()

    if selected_dir:
        session_config = tmux.build_session_config(selected_dir)
        tmux.create_tmux_session(session_config)
    else:
        print("No directory was selected", file=sys.stderr)
