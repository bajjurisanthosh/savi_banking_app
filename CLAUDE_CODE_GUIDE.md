# Claude Code Mastery Guide
### Learned using the SaVi Banking App as base project

---

## Table of Contents
1. [CLAUDE.md & Project Config](#1-claudemd--project-config)
2. [MCPs — Model Context Protocol](#2-mcps--model-context-protocol)
3. [Skills — Custom Slash Commands](#3-skills--custom-slash-commands)
4. [Git Worktrees](#4-git-worktrees)
5. [Sub-agents](#5-sub-agents)
6. [Agent Teams](#6-agent-teams)
7. [Token Management](#7-token-management)
8. [Hooks](#8-hooks)
9. [Plugins — 13 New Tools](#9-plugins--13-new-tools)

---

## 1. CLAUDE.md & Project Config

### What it is
`CLAUDE.md` is a markdown file at the project root that Claude Code reads **automatically at the start of every session**. It gives Claude persistent context about your project without re-explaining anything.

### File hierarchy
```
~/.claude/settings.json              ← global config (applies everywhere)
banking_app/.claude/settings.json    ← project config (overrides global)
banking_app/CLAUDE.md                ← project context (auto-loaded)
banking_app/.mcp.json                ← shared MCP servers (safe to commit)
```

### What goes in CLAUDE.md
- Project overview and stack
- How to run the app
- Key file locations and purposes
- Architectural decisions and conventions
- Account IDs, demo credentials, etc.
- Anything you'd have to re-explain every session

### Project-level `.claude/` directory
```
.claude/
├── settings.json     ← MCPs, permissions, hooks
├── commands/         ← custom slash commands (one .md file = one /command)
├── hooks/            ← shell scripts triggered on tool events
└── changes.log       ← auto-written by hooks
```

### Key insight
Every line in CLAUDE.md saves you tokens and time. A well-written CLAUDE.md means you can start any session with "continue from where we left off" and Claude knows exactly what to do.

---

## 2. MCPs — Model Context Protocol

### What it is
MCPs are external servers that expose tools to Claude Code — letting it interact with GitHub, SQLite, filesystems, Gmail, and more as naturally as it uses Read/Write/Bash.

### How MCPs work
```
Claude Code  →  MCP server (stdio subprocess)  →  external service
             ←  tool results                   ←
```

### Config locations by sensitivity
| File | Scope | Committed? | Used for |
|------|-------|-----------|----------|
| `.mcp.json` | Project, shared | **Yes** | Safe MCPs (no secrets) |
| `.claude/settings.json` | Project, private | **No** | Project-specific paths |
| `~/.claude/settings.json` | Global, private | **No** | Secrets (API tokens) |

### Configured MCPs for SaVi
```json
// .mcp.json — safe to commit
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "/Users/santhoshbajjuri/banking_app"]
    }
  }
}

// ~/.claude/settings.json — global, private
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}

// .claude/settings.json — project, private
{
  "mcpServers": {
    "sqlite": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite",
               "/Users/santhoshbajjuri/banking_app/banking.db"]
    }
  }
}
```

### Token secret pattern
Never hardcode tokens. Use environment variable expansion:
```json
"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
```
Store the actual value in `.env` (gitignored), auto-export from `~/.zshrc`:
```bash
export GITHUB_TOKEN=$(grep ^GITHUB_TOKEN ~/banking_app/.env | cut -d= -f2)
```

### Verify MCPs are connected
```bash
claude mcp list
```

---

## 3. Skills — Custom Slash Commands

### What it is
Skills are `.md` files in `.claude/commands/`. Each file becomes a `/command-name` you can invoke inside Claude Code. They are **reusable prompt templates** — write once, use forever.

### How they work
```
.claude/commands/security-audit.md  →  /security-audit
.claude/commands/add-route.md       →  /add-route
.claude/commands/banking-test.md    →  /banking-test
```

The filename becomes the command name. The file contents are the prompt, executed verbatim when invoked.

### `$ARGUMENTS` — passing parameters
```markdown
<!-- add-route.md -->
Add a new Flask route to the SaVi banking app.
User's request: $ARGUMENTS
```
Then invoke as:
```
/add-route bill pay page at /bill-pay, POST+GET, requires login
```
`$ARGUMENTS` gets replaced with everything after the command name.

### Skills built for SaVi
| Command | File | What it does |
|---------|------|-------------|
| `/add-route` | `add-route.md` | Scaffolds Flask route + template with auth |
| `/security-audit` | `security-audit.md` | OWASP Top 10 check with findings table |
| `/banking-test` | `banking-test.md` | Runs pytest, summarizes results |

### Running skills
**In Claude Code CLI** (terminal):
```bash
cd ~/banking_app && claude
/security-audit
```
**In a conversation**: just tell Claude to run it — "run /security-audit"

### Where skills live
- `~/.claude/commands/` → global (available in all projects)
- `banking_app/.claude/commands/` → project-only (only in this project)

---

## 4. Git Worktrees

### What it is
Git worktrees let you have **multiple working directories** attached to the same repository, each on a different branch, simultaneously — without stashing or switching.

### Worktrees vs Branches vs Forks
```
Fork       = copy of repo to different GitHub account (different remote)
Branch     = pointer to different commit in SAME repo
Worktree   = separate directory checked out to a branch of SAME repo
```

### Core commands
```bash
# Create a worktree on a new branch
git worktree add .claude/worktrees/bill-pay -b feature/bill-pay

# Create a worktree on an existing branch
git worktree add .claude/worktrees/review-pr feature/bill-pay

# List all active worktrees
git worktree list

# Remove a worktree (after merging)
git worktree remove .claude/worktrees/bill-pay
git branch -d feature/bill-pay
```

### Scenario 1: Hotfix while feature work is in progress
```bash
# Feature in progress on investments branch — don't touch it
# Bug reported in production:
git worktree add .claude/worktrees/hotfix -b hotfix/transfer-validation
# Fix the bug in .claude/worktrees/hotfix/
# Commit on hotfix branch
# Merge into main — investments branch never touched
git merge hotfix/transfer-validation
git worktree remove .claude/worktrees/hotfix
```

### Scenario 2: Two features built simultaneously
```bash
git worktree add .claude/worktrees/bill-pay      -b feature/bill-pay
git worktree add .claude/worktrees/investments   -b feature/investments
# Both in progress at the same time in different directories
# One developer (or one Claude agent) per directory
```

### Scenario 3: Two app versions running simultaneously
```bash
# Terminal 1 — stable main on port 5000
cd ~/banking_app && python app.py

# Terminal 2 — feature branch on port 5001
cd ~/banking_app/.claude/worktrees/investments
FLASK_RUN_PORT=5001 python app.py
# Compare both in browser simultaneously
```

### Scenario 4: Throwaway experiment
```bash
git worktree add .claude/worktrees/experiment -b experiment/sqlite-migration
# Make risky changes...
# If it works → git merge experiment/sqlite-migration
# If it fails → delete with no trace on main
git worktree remove .claude/worktrees/experiment
git branch -D experiment/sqlite-migration
```

### Scenario 5: Release branch maintenance
```bash
git worktree add .claude/worktrees/release-v1 release/v1
# Patch v1 in release worktree while v2 continues on main
# Tag releases from the release worktree
```

### Key rule
**One branch = one directory = one running server = one Claude agent**
This is the foundation for Agent Teams (Step 6).

### Claude Code EnterWorktree
```
/worktree feature-name
```
Creates `.claude/worktrees/<name>/`, switches the session into it, and tracks it. On exit you're asked to keep or remove.

---

## 5. Sub-agents

### What it is
Sub-agents are separate Claude instances spawned by the main Claude. They have their **own context window**, run independently, and return a single result.

### Why use them
1. **Protect context** — large file reads don't flood your main conversation
2. **Specialization** — each agent type has a specific skill set
3. **Parallelism** — run multiple agents simultaneously (Step 6)

### Four agent types
| Type | Best for | Key capability |
|------|----------|---------------|
| `Explore` | Read-only codebase research, fast searches | Reads files, runs grep, returns summaries |
| `Plan` | Architecture design, implementation planning | Designs systems, writes to plan file |
| `general-purpose` | Full autonomous tasks | Read + write + run commands + full tools |
| `claude-code-guide` | Questions about Claude Code itself | Web search, docs lookup |

### Usage
```python
# Foreground — wait for result
Agent(subagent_type="Explore",
      prompt="Map all Flask routes in app.py and what templates they render")

# Background — don't block, get notified when done
Agent(subagent_type="general-purpose",
      run_in_background=True,
      prompt="Implement the alerts feature...")
```

### Token math
```
Without agents:
  Read 10 files (5000 tokens) → stays in main context forever
  Main context cost: 5000+ tokens consumed permanently

With Explore agent:
  Agent reads 10 files in its own context (5000 tokens there)
  Returns 200-token summary to main context
  Main context cost: 200 tokens
```

### Resuming agents
Every agent returns an `agentId`. You can resume it later:
```python
Agent(subagent_type="general-purpose", resume="ae7e670b885857365",
      prompt="Continue from where you left off, now also add tests")
```

---

## 6. Agent Teams

### What it is
Agent Teams = multiple sub-agents running in parallel, each in an isolated worktree, each building a different feature simultaneously.

### The pattern
```
You (orchestrator)
├── Agent 1 (background + isolated worktree) → Feature A
├── Agent 2 (background + isolated worktree) → Feature B
└── Agent 3 (background + isolated worktree) → Feature C

    ... do other work or wait ...

All finish → review each branch → merge what looks good
```

### The `isolation: "worktree"` parameter
```python
Agent(
    subagent_type="general-purpose",
    isolation="worktree",    # auto-creates a git worktree for this agent
    run_in_background=True,  # doesn't block main Claude
    prompt="Build the alerts feature..."
)
```
Each agent gets its own copy of the repo. Changes are committed to an auto-named branch. The worktree path is returned when done.

### Merge workflow after agents finish
```bash
git log --oneline --all --graph   # see all agent branches
git merge worktree-agent-ae7e670b  # merge alerts feature
git merge worktree-agent-a1e94baa  # merge profile feature
# Resolve conflicts if any, then commit
git worktree remove .claude/worktrees/agent-ae7e670b
git worktree remove .claude/worktrees/agent-a1e94baa
```

### Handling conflicts
Both agents touching the same file (e.g., `app.py`) causes a merge conflict. Solutions:
1. **Better isolation** — use Flask blueprints so agents write to separate files
2. **Sequential merges** — merge agent 1 first, give agent 2 the updated code
3. **Explicit line ranges** — tell each agent exactly where in the file to insert code

### What was built in parallel for SaVi
- **Agent 1**: Transaction Alerts — `mock_data.py` + `/alerts` route + `alerts.html` + dashboard banners
- **Agent 2**: User Profile — `/profile` route + `profile.html` + CSS + navbar link
- Both ran simultaneously (~144s wall clock vs ~252s sequential)

---

## 7. Token Management

### What tokens are
Every message, file read, tool result, and code block in a conversation occupies tokens. Context window = finite. Tokens = cost and speed.

### The 3 commands
| Command | When to use | Effect |
|---------|-------------|--------|
| `/compact` | Mid-task, context getting big | Summarizes history, keeps recent, frees space |
| `/clear` | Switching to unrelated task | Wipes everything, fresh start |
| `/cost` | Curious about usage | Shows token count and cost for session |

### When Claude Code auto-compacts
When approaching context limits, Claude Code automatically compresses older messages. You'll see:
```
[Context compressed: conversation summarized to save space]
```
You can trigger this manually before it's needed with `/compact` to control what gets preserved.

### 5 practical patterns

**Pattern 1: CLAUDE.md = free context restore**
```
New session → Claude reads CLAUDE.md (500 tokens)
Knows: stack, routes, conventions, account IDs
Saves: 2000+ tokens of re-explanation
```

**Pattern 2: Sub-agents protect main context**
```python
# Expensive: reads stay in main context forever
Read("app.py")  # 291 lines → ~3000 tokens in context

# Efficient: sub-agent takes the hit
Agent(subagent_type="Explore", prompt="Analyze app.py")
# → returns 200-token summary to main context
```

**Pattern 3: Scoped reads**
```python
Read("app.py")                        # 291 lines — expensive
Read("app.py", offset=119, limit=20)  # 20 lines — cheap
Grep(pattern="def transfer")          # just the location — cheapest
```

**Pattern 4: Parallel agents = same tokens, half the time**
```
Sequential: Agent A (100s) + Agent B (100s) = 200s
Parallel:   Agent A + Agent B simultaneously = 100s
Same total tokens, 2× faster
```

**Pattern 5: Compact before implementation**
```
Exploration phase: lots of file reads, searching, planning
→ /compact (keep the plan, discard the raw search results)
Implementation phase: clean context, focused on building
```

---

## 8. Hooks

### What it is
Hooks are shell commands that run automatically when Claude Code fires tool events. They enforce rules, auto-validate, log, or block actions without you having to ask every time.

### 4 hook events
| Event | Runs | Can block? |
|-------|------|-----------|
| `PreToolUse` | Before a tool executes | Yes (exit 2) |
| `PostToolUse` | After a tool executes | Feedback only |
| `Notification` | When Claude sends a notification | No |
| `Stop` | When the session ends | No |

### Exit codes
- `exit 0` — success, Claude continues normally
- `exit 2` — block (PreToolUse) or alert Claude (PostToolUse), Claude sees stdout and reacts

### Hook input
Hooks receive a JSON payload via `stdin`:
```json
{
  "session_id": "...",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": { "file_path": "/path/to/file.py" },
  "tool_response": { ... }
}
```

### Configured hooks for SaVi
```
.claude/hooks/
├── block-env-read.py        PreToolUse  → Read       Blocks .env reads (security)
├── block-dangerous-bash.py  PreToolUse  → Bash       Blocks rm -rf, force push, reset --hard
├── syntax-check.py          PostToolUse → Write|Edit Catches Python syntax errors immediately
├── auto-format.py           PostToolUse → Write|Edit Runs black silently after every edit
├── change-log.py            PostToolUse → Write|Edit|Bash  Audit trail in .claude/changes.log
└── session-summary.py       Stop        → (all)      Summary + archives to session-history.log
```

### Hook configuration in settings.json
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/block-env-read.py" }]
      },
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/block-dangerous-bash.py" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/syntax-check.py" },
          { "type": "command", "command": "python3 .claude/hooks/auto-format.py" }
        ]
      },
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/change-log.py" }]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/session-summary.py" }]
      }
    ]
  }
}
```

### Hook execution flow for a single file edit
```
Claude edits app.py
       ↓
[PreToolUse]  — none configured for Edit
Claude writes the file
[PostToolUse] fires in order:
  1. syntax-check.py   → error? Claude sees it and fixes immediately
  2. auto-format.py    → black runs silently
  3. change-log.py     → entry appended to changes.log
Session ends:
  4. session-summary.py → prints + archives summary
```

### Matcher patterns
- `"Write"` — exact tool name
- `"Write|Edit"` — regex OR
- `"Bash"` — all Bash calls
- `""` — matches every tool (use for Stop hooks)

---

## 9. Plugins — 13 New Tools

### What a plugin is
A plugin packages everything from Steps 1–8 into a **shareable, versioned, installable unit**. It's the difference between "config that lives on my machine" and "config anyone can install in one command."

```
savi-banking-plugin/
├── .claude-plugin/plugin.json   ← manifest (name, version, author)
├── commands/                    ← slash commands (Step 3)
├── skills/                      ← agent skills (auto-invoked by Claude)
├── agents/                      ← custom sub-agent definitions (Step 5)
├── hooks/hooks.json             ← event hooks (Step 8)
├── .mcp.json                    ← MCP servers (Step 2)
└── settings.json                ← default permissions/settings
```

### Standalone config vs Plugin
| | Standalone `.claude/` | Plugin |
|--|-----------------------|--------|
| Scope | One project | Shareable across projects + teams |
| Skill name | `/security-audit` | `/savi-banking:security-audit` |
| Install | Manual file copy | `/plugin install name@marketplace` |
| Updates | Edit files manually | Version bump + reinstall |
| Namespace | None (conflicts possible) | Always namespaced (no conflicts) |

### The 13 plugins at claude.com/plugins
| # | Plugin | Type | What it does |
|---|--------|------|-------------|
| 1 | **Frontend Design** | Skills | Polished UI code, avoids generic AI aesthetics |
| 2 | **Context7** | MCP | Live version-specific docs pulled into context |
| 3 | **Superpowers** | Skills+Agents | Brainstorming, TDD, debugging, skill authoring |
| 4 | **Code Review** | Agents | PR review with confidence-based filtering |
| 5 | **GitHub** | MCP | Issues, PRs, code search, full GitHub API |
| 6 | **Feature Dev** | Agents | Explore → design → implement → review |
| 7 | **Code Simplifier** | Skills | Refines changed code without breaking it |
| 8 | **Ralph Loop** | Agents | Iterative loops until task completion |
| 9 | **Playwright** | MCP | Browser automation, screenshots, form filling |
| 10 | **TypeScript LSP** | LSP | Real-time TS/JS code intelligence |
| 11 | **Commit Commands** | Commands | `/commit`, `/push`, `/pr` workflow |
| 12–13 | Community | Various | Via `/plugin > Discover` |

### Enterprise domain plugins (Claude Cowork)
| Domain | Capabilities |
|--------|-------------|
| **Finance** | Market research, financial modeling, Excel→PPT reporting |
| **Legal** | Contract review, risk flagging, compliance drafting |
| **HR** | Candidate screening, offer letters, onboarding automation |
| **Engineering** | Incident response, root cause analysis, release checklists |
| **Sales & Marketing** | Lead enrichment, outreach, campaign planning |
| **Design** | Design system enforcement, component generation |

### Install a plugin
```bash
# From the official marketplace
/plugin install github@claude-plugin-directory

# From a local directory (development)
claude --plugin-dir ./savi-banking-plugin

# Multiple plugins
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two

# List installed plugins
/plugin list

# Discover marketplace
/plugin discover
```

### Build a plugin
```bash
mkdir my-plugin && mkdir my-plugin/.claude-plugin

# 1. Create manifest
cat > my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "description": "What it does",
  "version": "1.0.0"
}
EOF

# 2. Add commands (slash commands)
mkdir my-plugin/commands
echo "Do something useful. Args: \$ARGUMENTS" > my-plugin/commands/do-thing.md

# 3. Add a skill (auto-invoked by Claude)
mkdir -p my-plugin/skills/my-skill
cat > my-plugin/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Does X. Use when user asks about Y.
---
Instructions for what to do...
EOF

# 4. Test locally
claude --plugin-dir ./my-plugin
# → invoke with /my-plugin:do-thing args here
```

### The SaVi banking plugin (built in this session)
```
savi-banking-plugin/
├── .claude-plugin/plugin.json              ← manifest
├── commands/security-audit.md             → /savi-banking:security-audit
├── commands/add-route.md                  → /savi-banking:add-route
├── commands/banking-test.md               → /savi-banking:banking-test
├── skills/analyze-transactions/SKILL.md   ← auto-invoked for spending analysis
├── hooks/hooks.json                       ← .env block + bash safety + syntax check
└── .mcp.json                              ← filesystem MCP
```

Test it:
```bash
claude --plugin-dir ./savi-banking-plugin
# Then:
/savi-banking:security-audit
/savi-banking:add-route loan calculator page at /loans
```

### Key insight: plugins unify everything
A plugin is not a new concept — it's a **packaging format** for all the features in Steps 1–8:
- MCPs (Step 2) → `.mcp.json`
- Skills/commands (Step 3) → `commands/` + `skills/`
- Sub-agent definitions (Step 5) → `agents/`
- Hooks (Step 8) → `hooks/hooks.json`
- Settings/permissions (Step 1) → `settings.json`

The plugin system lets you share this entire setup with one command.

---

## Project Structure After All Steps

```
banking_app/
├── CLAUDE.md                        ← auto-loaded context (Step 1)
├── CLAUDE_CODE_GUIDE.md             ← this document
├── .mcp.json                        ← shared MCP servers (Step 2)
├── .env                             ← GITHUB_TOKEN (gitignored)
├── .gitignore
├── requirements.txt
├── app.py                           ← Flask routes (grew through Steps 4-6)
├── mock_data.py                     ← in-memory data + alerts/notifications
├── templates/
│   ├── base.html
│   ├── dashboard.html               ← alert banners added (Step 6)
│   ├── alerts.html                  ← new (Step 6, Agent 1)
│   ├── profile.html                 ← new (Step 6, Agent 2)
│   ├── bill_pay.html                ← new (Step 4)
│   ├── investments.html             ← new (Step 4)
│   └── [other templates]
├── static/css/style.css             ← alerts + profile CSS added
└── .claude/
    ├── settings.json                ← MCPs + permissions + hooks (Steps 2, 8)
    ├── commands/                    ← custom slash commands (Step 3)
    │   ├── add-route.md             → /add-route
    │   ├── security-audit.md        → /security-audit
    │   └── banking-test.md          → /banking-test
    ├── hooks/                       ← event-driven automation (Step 8)
    │   ├── block-env-read.py
    │   ├── block-dangerous-bash.py
    │   ├── syntax-check.py
    │   ├── auto-format.py
    │   ├── change-log.py
    │   └── session-summary.py
    ├── changes.log                  ← per-session audit trail
    ├── session-history.log          ← archived session summaries
    └── worktrees/                   ← git worktrees (Step 4)
        ├── bill-pay/                → feature/bill-pay
        └── investments/             → feature/investments
```

## Git Branch History

```
*   a66753e  main  ← profile + alerts merged
|\
| * b5199ee  feature/profile (Agent 2)
* |   7399e07  alerts merged
|\ \
| * | c07c457  feature/alerts (Agent 1)
| |/
* |   33f699e  hotfix merged
|\ \
| |/
|/|
| * 5db4cd6  hotfix/transfer-validation
|/
| * d0f2437  feature/investments
|/
| * ab1f7e2  feature/bill-pay
|/
* 9d5683b   Initial commit
```

---

## Quick Reference

### Commands
```bash
/compact          # compress conversation history
/clear            # fresh start
/cost             # show token usage
/worktree name    # create isolated worktree and enter it
/security-audit   # run OWASP audit on SaVi
/add-route ...    # scaffold new Flask route
/banking-test     # run test suite
```

### Agent types at a glance
```python
Agent(subagent_type="Explore")         # fast read-only research
Agent(subagent_type="Plan")            # architecture and planning
Agent(subagent_type="general-purpose") # full implementation
Agent(subagent_type="claude-code-guide") # Claude Code questions
```

### Hook exit codes
```
exit 0  →  proceed normally
exit 2  →  block (PreToolUse) / alert Claude (PostToolUse)
```

### MCP config locations
```
~/.claude/settings.json        →  global private (tokens, secrets)
.claude/settings.json          →  project private (db paths, project MCPs)
.mcp.json                      →  project shared (safe to commit)
```
