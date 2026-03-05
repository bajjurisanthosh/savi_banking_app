# SaVi Banking App

## Project Overview
SaVi is a demo Flask banking web application. It serves as a **learning base for Claude Code features**: MCPs, skills, worktrees, sub-agents, hooks, and plugins.

## Stack
- Python / Flask 3.x
- Jinja2 templates (server-rendered, no JS framework)
- In-memory mock data (`mock_data.py`) — no database yet
- No external dependencies beyond Flask

## Running the App
```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## Demo Login
- Email: `demo@savi.com`
- Password: `password123`

## Key Files
| File | Purpose |
|------|---------|
| `app.py` | All Flask routes and auth logic |
| `mock_data.py` | In-memory users, accounts, transactions |
| `templates/` | Jinja2 HTML templates |
| `static/` | CSS and JS assets |
| `.claude/settings.json` | Project-level Claude Code config |
| `.claude/commands/` | Custom slash commands (project skills) |

## Architecture
- Auth via Flask sessions; `login_required` decorator in `app.py:15`
- All data is in-memory — resets on server restart
- `TRANSACTIONS` is a mutable list; transfers append to it at runtime
- Flash messages use categories: `success`, `error`, `warning`, `info`

## Account IDs (for queries/filters)
- `chk001` — Checking
- `sav001` — Savings
- `cc001` — Credit Card

## Conventions
- New protected routes: add `@login_required` decorator
- New transactions: follow the dict shape in `mock_data.py:_make_transactions()`
- Keep all routes in `app.py` until the app grows large enough to need blueprints

## Token-Efficient Patterns
- Use `Grep` + `Read(offset, limit)` instead of reading whole files
- Use `Explore` sub-agents for codebase research — they return summaries, not raw file contents
- `/compact` after exploration phase, before implementation
- `/clear` when switching to a completely unrelated task
- This CLAUDE.md auto-loads every session — no need to re-explain the project

## Claude Code Learning Roadmap
This project is used to learn the following Claude Code features in order:

1. **CLAUDE.md & project config** ← you are here
2. **MCPs** — GitHub, Filesystem, SQLite MCP servers
3. **Skills** — custom slash commands in `.claude/commands/`
4. **Git Worktrees** — isolated feature branches via `EnterWorktree`
5. **Sub-agents** — Explore / Plan / general-purpose agents
6. **Agent Teams** — background agents on parallel worktrees
7. **Token Management** — `/compact`, `/clear`, context efficiency
8. **Hooks** — shell commands triggered on tool events
9. **Plugins** — the 13 new tool types in Claude Code
