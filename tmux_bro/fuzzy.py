import subprocess
from .config import load_global_config


def run_fuzzy_finder():
    """
    Run zoxide with fzf to select a directory.
    If zoxide is not installed, use projects_dir from config as fallback.
    """
    try:
        # Check for fzf dependency
        try:
            subprocess.run(["fzf", "--version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Error: fzf is not installed or not in PATH")
            input("Press Enter to continue...")
            return None

        # Try to use zoxide if available
        try:
            process = subprocess.Popen(
                "zoxide query -l | fzf",
                shell=True,
                stdout=subprocess.PIPE,
                text=True,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            # Use projects_dir from config as fallback
            config = load_global_config()
            projects_dir = config.get("projects_dir")
            if not projects_dir:
                print(
                    "Error: zoxide is not installed and projects_dir is not set in ~/.config/tmux-bro.yaml"
                )
                input("Press Enter to continue...")
                return None

            process = subprocess.Popen(
                f"find {projects_dir} -type d -maxdepth 1 | fzf",
                shell=True,
                stdout=subprocess.PIPE,
                text=True,
            )

        output = process.communicate()[0].strip().split("\n")

        if not output or not output[0]:
            return None

        # Parse the output based on whether a key was pressed
        if len(output) == 1:
            return output[0]
        else:
            return output[1]

    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to continue...")
        return None, None
