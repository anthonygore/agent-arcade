# AI Arcade

Play terminal games while your AI coding agent thinks. AI Arcade is a CLI that launches a dual-pane tmux session: your AI agent runs up top, and a game runner lives below, with clear status cues when the agent is ready.

## Why
- Kill dead time while waiting on AI agents
- Stay in the terminal (no context switching to phone or browser)
- Seamless pane switching with familiar tmux keybindings

## Highlights
- Single command launcher: `ai-arcade`
- Dual-pane tmux layout (agent + game runner)
- Built-in presets for popular AI CLIs (Claude Code, Aider, Copilot CLI, Cursor)
- AI readiness detection via output pattern monitoring
- Curated terminal games (initially nbsdgames)
- YAML config at `~/.ai-arcade/config.yaml`

## How It Works
1. Run `ai-arcade`
2. Pick an AI agent (or Games Only)
3. AI Arcade creates a tmux session
4. Top pane: your AI agent (unmodified)
5. Bottom pane: game selector + game session
6. Status bar indicates AI state (Thinking / Ready)

## Installation (planned)
- `pip install ai-arcade`
- Optional Homebrew formula for macOS

A post-install setup script will:
- Install tmux if missing
- Download/compile nbsdgames
- Create `~/.ai-arcade/` config and metadata

## Configuration
Default config path: `~/.ai-arcade/config.yaml`

Key options:
- AI agent commands and ready patterns
- Pane switching keybindings
- Game library location
- Notifications (visual/audio)
- AI check interval

## Planned Architecture
- Python 3.9+
- tmux for multiplexing
- Textual or curses for the TUI
- YAML config (PyYAML)
- Game metadata via JSON or SQLite

## Roadmap
- MVP: launcher menu, tmux session, game runner
- AI monitoring: output pattern detection + notifications
- UX polish: title screen, shortcuts, session resume
- Distribution: PyPI package + install script

## Status
Early design phase (see `1 - PROJECT  OVERVIEW.md` for full spec).

## Contributing
Contribution guidelines will be added once the MVP stabilizes.

## License
TBD
