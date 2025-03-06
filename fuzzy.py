import subprocess
import os


def run_fuzzy_finder():
    """
    Run zoxide with fzf to select a directory.
    If zoxide is not installed, use $TMUX_BRO_PROJECTS_DIR as fallback.
    """
    try:
        # Check for fzf dependency
        try:
            subprocess.run(["fzf", "--version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Error: fzf is not installed or not in PATH")
            input("Press Enter to continue...")
            return None, None

        # Try to use zoxide if available
        try:
            process = subprocess.Popen(
                "zoxide query -l | fzf", shell=True, stdout=subprocess.PIPE, text=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            # Use TMUX_BRO_PROJECTS_DIR as fallback
            projects_dir = os.environ.get("TMUX_BRO_PROJECTS_DIR")
            if not projects_dir:
                print(
                    "Error: zoxide is not installed or TMUX_BRO_PROJECTS_DIR is not set"
                )
                input("Press Enter to continue...")
                return None, None

            process = subprocess.Popen(
                f"find {projects_dir} -type d -maxdepth 1 | fzf",
                shell=True,
                stdout=subprocess.PIPE,
                text=True,
            )

        output = process.communicate()[0].strip().split("\n")

        if not output or not output[0]:
            return None, None

        # Parse the output based on whether a key was pressed
        if len(output) == 1:
            return output[0], ""  # No key pressed, just selection
        else:
            return output[1], output[0]  # Key pressed + selection

    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to continue...")
        return None, None
