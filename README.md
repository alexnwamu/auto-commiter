# 🚀 Auto-Commiter

**AI-powered commit message generator** - One command to generate smart commit messages, commit, and push.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- **🤖 Smart message generation** - Uses rule-based analysis or OpenAI to generate meaningful commit messages
- **📝 Conventional Commits** - Follows the [Conventional Commits](https://www.conventionalcommits.org/) specification
- **⚡ Caching** - Caches messages for similar diffs to avoid redundant API calls
- **🔧 Configurable** - Remember your preferences (style, auto-push, model choice)
- **🎯 One command** - Stage, generate, commit, and push with a single command

---

## 📦 Installation

### Option 1: Install with pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) installs the tool in an isolated environment:

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install auto-commiter
pipx install git+https://github.com/yourusername/auto-commiter.git
```

### Option 2: Install with pip

```bash
pip install git+https://github.com/yourusername/auto-commiter.git
```

### Option 3: Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-commiter.git
cd auto-commiter

# Install in development mode
pip install -e .

# Or using uv (fast Python package manager)
uv pip install -e .
```

### Option 4: Direct download

```bash
# Download and run directly
curl -sSL https://raw.githubusercontent.com/yourusername/auto-commiter/main/install.sh | bash
```

---

## 🚀 Quick Start

### Basic Usage

```bash
# Stage all changes, generate a commit message, commit, and push
autocommit

# Generate and commit without pushing
autocommit --no-push

# Stage changes and commit (without auto-staging)
git add .
autocommit --no-push
```

### Configuration

```bash
# View current configuration
autocommit config

# Set default style (conventional, short, verbose)
autocommit config style conventional

# Enable/disable auto-push
autocommit config auto_push true

# Enable/disable auto-staging
autocommit config auto_stage true

# Set default model (auto, rule-based, openai)
autocommit config model rule-based

# Reset all settings to defaults
autocommit config --reset
```

### Cache Management

```bash
# View cache statistics
autocommit cache

# Clear the cache
autocommit cache --clear
```

---

## ⚙️ Options

| Option | Short | Description |
|--------|-------|-------------|
| `--style` | `-s` | Commit style: `conventional`, `short`, `verbose` |
| `--model` | `-m` | Model: `auto`, `rule-based`, `openai` |
| `--stage` | `-a` | Stage all changes before committing |
| `--push` | `-p` | Push after committing |
| `--no-push` | | Don't push (overrides config) |
| `--single` | | Generate only one message option |
| `--no-cache` | | Don't use cached messages |
| `--preview` | | Show diff preview before generating |
| `--version` | `-v` | Show version |

---

## 📋 Commit Styles

### Conventional (default)
```
feat(auth): add OAuth2 login support
```

### Short
```
add OAuth2 login support in auth
```

### Verbose
```
feat(auth): add OAuth2 login support

Changed files:
  + src/auth/oauth.py (new)
  * src/auth/login.py (+45, -12)
```

---

## 🔧 Configuration

Settings are stored in `~/.autocommit/settings.json`:

| Setting | Default | Description |
|---------|---------|-------------|
| `style` | `conventional` | Default commit message style |
| `auto_push` | `false` | Auto-push after commit |
| `auto_stage` | `true` | Auto-stage all changes |
| `use_cache` | `true` | Cache messages for similar diffs |
| `model` | `auto` | Model selection (`auto`, `rule-based`, `openai`) |
| `max_diff_for_rules` | `5000` | Max diff size for rule-based model |
| `confirm_before_commit` | `true` | Confirm before committing |

---

## 🔑 OpenAI Setup (Optional)

The tool works without OpenAI using the rule-based model. But for large diffs or better quality:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key
   ```

---

## 📊 How It Works

1. **Stage Changes** - Optionally stages all changes (`git add --all`)
2. **Get Diff** - Reads the staged diff (`git diff --cached`)
3. **Check Cache** - Looks for cached message for similar diff
4. **Select Model** - Chooses rule-based or OpenAI based on diff size
5. **Generate Message** - Creates commit message following selected style
6. **User Confirmation** - Shows message options for selection
7. **Commit & Push** - Commits and optionally pushes

### Rule-Based Model

For smaller diffs, the tool uses intelligent pattern matching:

- **File patterns** - Detects docs, tests, configs from file paths
- **Content analysis** - Scans for keywords like "fix", "add", "refactor"
- **Change metrics** - Uses added/removed line counts
- **Scope inference** - Extracts scope from directory structure

### Cache System

- Caches commit messages by diff hash
- 30-day TTL with 500 entry limit
- Stored in `~/.autocommit/cache.json`
- Hit rate tracked for optimization

---

## 🛠️ Development

```bash
# Clone repo
git clone https://github.com/yourusername/auto-commiter.git
cd auto-commiter

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (use `autocommit` of course! 😄)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 💡 Tips

- Use `--single` for faster commits when you trust the generator
- Set `auto_push false` if you prefer to review before pushing
- Use `--preview` to see what changes will be committed
- The rule-based model is fast and works offline
- Cache helps when making similar changes repeatedly

---

Made with ❤️ for developers who hate writing commit messages
