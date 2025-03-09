import os
import yaml
import json
import glob
import toml
from typing import List, Optional


def detect_workspace(directory: str) -> Optional[List[str]]:
    """
    Detect if the directory is any type of workspace (pnpm, npm, cargo, etc.)
    Returns a list of package directories if it's a workspace, None otherwise
    """
    # Try each workspace type in order
    detectors = [
        detect_pnpm_workspace,
        detect_npm_workspace,
        detect_cargo_workspace,
    ]

    for detector in detectors:
        package_dirs = detector(directory)
        if package_dirs:
            return package_dirs

    return None


def detect_npm_workspace(directory: str) -> Optional[List[str]]:
    """
    Detect if the directory is an npm workspace by checking for workspaces in package.json
    Returns a list of package directories if it's a workspace, None otherwise
    """
    package_json_path = os.path.join(directory, "package.json")

    if not os.path.isfile(package_json_path):
        return None

    try:
        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        if not package_data or "workspaces" not in package_data:
            return None

        workspaces = package_data["workspaces"]
        package_dirs = []

        # Handle both array and object formats
        if isinstance(workspaces, list):
            workspace_patterns = workspaces
        elif isinstance(workspaces, dict) and "packages" in workspaces:
            workspace_patterns = workspaces["packages"]
        else:
            return None

        for pattern in workspace_patterns:
            # Simple case - no glob patterns
            if "*" not in pattern:
                package_dir = os.path.join(directory, pattern)
                if os.path.isdir(package_dir):
                    package_dirs.append(package_dir)
            else:
                # Basic glob support
                glob_pattern = os.path.join(directory, pattern)
                matching_dirs = [d for d in glob.glob(glob_pattern) if os.path.isdir(d)]
                package_dirs.extend(matching_dirs)

        return package_dirs if package_dirs else None

    except Exception:
        return None


def detect_pnpm_workspace(directory: str) -> Optional[List[str]]:
    """
    Detect if the directory is a pnpm workspace by checking for pnpm-workspace.yaml
    Returns a list of package directories if it's a workspace, None otherwise
    """
    workspace_file = os.path.join(directory, "pnpm-workspace.yaml")

    if not os.path.isfile(workspace_file):
        return None

    try:
        with open(workspace_file, "r") as f:
            workspace_config = yaml.safe_load(f)

        if not workspace_config or "packages" not in workspace_config:
            return None

        packages = workspace_config["packages"]
        package_dirs = []

        for package_pattern in packages:
            if "*" not in package_pattern:
                package_dir = os.path.join(directory, package_pattern)
                if os.path.isdir(package_dir):
                    package_dirs.append(package_dir)
            else:
                # Basic glob support
                glob_pattern = os.path.join(directory, package_pattern)
                matching_dirs = [d for d in glob.glob(glob_pattern) if os.path.isdir(d)]
                package_dirs.extend(matching_dirs)

        return package_dirs if package_dirs else None

    except Exception:
        return None


def detect_cargo_workspace(directory: str) -> Optional[List[str]]:
    """
    Detect if the directory is a Cargo workspace by checking for workspace members in Cargo.toml
    Returns a list of package directories if it's a workspace, None otherwise
    """
    cargo_toml_path = os.path.join(directory, "Cargo.toml")

    if not os.path.isfile(cargo_toml_path):
        return None

    try:
        with open(cargo_toml_path, "r") as f:
            cargo_data = toml.load(f)

        if not cargo_data or "workspace" not in cargo_data:
            return None

        workspace = cargo_data["workspace"]
        if "members" not in workspace:
            return None

        members = workspace["members"]
        package_dirs = []

        for member in members:
            package_dir = os.path.join(directory, member)
            if os.path.isdir(package_dir):
                package_dirs.append(package_dir)

        return package_dirs if package_dirs else None

    except Exception:
        return None


def has_cargo_toml(directory: str) -> bool:
    """
    Check if the directory has a Cargo.toml file
    """
    return os.path.isfile(os.path.join(directory, "Cargo.toml"))


def has_package_json_dev_script(package_dir: str) -> bool:
    """
    Check if the package.json in the given directory has a 'dev' script
    """
    package_json_path = os.path.join(package_dir, "package.json")

    if not os.path.isfile(package_json_path):
        return False

    try:
        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        return (
            package_data
            and "scripts" in package_data
            and "dev" in package_data["scripts"]
        )
    except Exception:
        return False


def detect_package_manager(directory: str) -> str:
    """
    Detect which package manager is used in the directory
    Returns 'pnpm', 'yarn', 'npm', or 'cargo' based on lock files
    """
    # Check for lock files
    if os.path.exists(os.path.join(directory, "pnpm-lock.yaml")):
        return "pnpm"
    if os.path.exists(os.path.join(directory, "yarn.lock")):
        return "yarn"
    if os.path.exists(os.path.join(directory, "package-lock.json")):
        return "npm"
    if os.path.exists(os.path.join(directory, "Cargo.lock")) or has_cargo_toml(
        directory
    ):
        return "cargo"

    # Default to npm if no lock file is found but package.json exists
    if os.path.exists(os.path.join(directory, "package.json")):
        return "npm"

    return "unknown"
