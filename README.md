# Agent Arcade

**Play fun arcade games while waiting on AI agent tasks!**

Stop context-switching to your phone while waiting for Claude Code or Codex to finish. Stay in the terminal, stay productive.

---

## Installation

### Step 1: Install Agent Arcade

**Via pipx (Recommended)** - installs in isolated environment:

```bash
# Install pipx if needed
brew install pipx  # macOS
# or: python3 -m pip install --user pipx

# Install agent-arcade
pipx install agent-arcade
```

**Updating**: `pipx upgrade agent-arcade`

**Via pip:**

```bash
pip install agent-arcade
```

**Updating**: `pip install --upgrade agent-arcade`

### Step 2: Install tmux (Required)

Agent Arcade requires tmux to create the dual-pane interface:

```bash
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt-get install tmux

# RedHat/CentOS
sudo yum install tmux
```

### Step 3: Run Agent Arcade

```bash
agent-arcade
```

### From Source (for development)

```bash
git clone https://github.com/anthonygore/agent-arcade
cd agent-arcade
poetry install
poetry run agent-arcade
```

---

## Quick Start

1. **Launch Agent Arcade**:
   ```bash
   agent-arcade
   ```

2. **Select your AI agent** from the menu (or choose "Games Only")

3. **Switch between windows**:
   - `Ctrl+Space` - Toggle between AI and Games windows

4. **Play games while AI thinks!** 🎮

---

## Built-in Games

### Snake
Classic arcade action. Eat food, grow longer, avoid walls and yourself!
- **Controls**: Arrow keys to move, P to pause, Q to quit
- **Goal**: Get the highest score possible

**More games coming soon!**

---

## Supported AI Agents

- Claude Code
- Cursor

Want to add more agents? Submit a PR.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Credits

- Built with [Textual](https://textual.textualize.io/) - Modern Python TUI framework
- Powered by [tmux](https://github.com/tmux/tmux) - Terminal multiplexer
- Inspired by the need to stay productive while AI agents think

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/anthonygore/agent-arcade/issues)
- **Discussions**: [GitHub Discussions](https://github.com/anthonygore/agent-arcade/discussions)

---
