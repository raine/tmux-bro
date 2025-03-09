import subprocess


def get_git_root(directory):
    """
    Get the root directory of the git repository containing the specified directory.
    Returns None if not in a git repository.
    """
    try:
        # Run git command in the specified directory
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            cwd=directory,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
