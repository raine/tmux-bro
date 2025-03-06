# tmux-bro

A smart (and opinionated) tmux session manager that sets up project-specific sessions automatically.

Think `tmuxp` but without predefined YAML configuration.

```
┌───────────────────────────┬───────────────────────────┐
│1| function main() {       │ $ npm run dev             │
│2|   console.log("Hello"); │ > project@1.0.0 dev       │
│3| }                       │ > vite                    │
│4|                         │                           │
│5|                         │ VITE v4.3.9 ready         │
│6|                         │ ➜ localhost:3000/         │
│7|    ┌──────────────┐     ├───────────────────────────┤
│8|    │   tmux-bro   │     │ $                         │
│9|    └──────────────┘     │                           │
│1|                         │                           │
│2|                         │                           │
│ NORMAL • main.js          │                           │
└───────────────────────────┴───────────────────────────┘
```

## Features

- Fuzzy find your projects with [fzf](https://github.com/junegunn/fzf) and [zoxide](https://github.com/ajeetdsouza/zoxide)
- Automatic workspace detection for npm, pnpm, yarn and Cargo
- Smart session layout based on project type
- Automatically runs `dev` script in a pane when available
- Handles Python virtual environments

## Installation

```sh
pip install git+https://github.com/raine/tmux-bro.git
```

## Dependencies

- [fzf](https://github.com/junegunn/fzf) for fuzzy finding
- [zoxide](https://github.com/ajeetdsouza/zoxide) (optional) for directory navigation

## Setup

### tmux popup bind (optional but recommended)

Set up a mapping in tmux configuration that runs `tmux-bro` in a popup:

```sh
bind C-t display-popup -E "tmux-bro"
```

### Project discovery

tmux-bro uses two approaches to discover your projects:

1. **zoxide** (recommended): If you have
   [zoxide](https://github.com/ajeetdsouza/zoxide) installed, tmux-bro will use
   it to find your most frequently accessed directories. This leverages your
   existing navigation habits without requiring additional configuration.

2. **TMUX_BRO_PROJECTS_DIR** (fallback): If zoxide is not available, tmux-bro
   will look for projects in the directory specified by the
   `TMUX_BRO_PROJECTS_DIR` environment variable. You should set this to the
   root directory where you keep your projects:

   ```sh
   # Add to your .bashrc, .zshenv, etc.
   export TMUX_BRO_PROJECTS_DIR="$HOME/projects"
   ```

   Note that tmux won't pick up that immediately in popups. You need to run
   `tmux set-environment -g TMUX_BRO_PROJECTS_DIR "$TMUX_BRO_PROJECTS_DIR"` or
   restart tmux.

Both approaches integrate with fzf to provide a fast fuzzy-search interface for selecting projects.

## Usage

Hit the tmux popup mapping or run `tmux-bro`.

This will:

1. Open a fuzzy finder to select a project directory
2. Detect the workspace type (npm, pnpm, Cargo, or plain)
3. Create a tmux session with appropriate layout for the project

### Environment Variables

- `EDITOR`: Your preferred editor
- `TMUX_BRO_PROJECTS_DIR`: Fallback directory to search for projects when zoxide is not available

## Example

When used with a npm monorepo, tmux bro will:

1. Create a tmux session named after your repository
2. Create separate windows for each package
3. In each window, set up:
   - Your editor in the main pane
   - A dev script running (if the package has one)
   - A clean shell

## License

MIT
