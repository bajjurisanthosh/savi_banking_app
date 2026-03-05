# SaVi Banking Plugin

Claude Code plugin for the SaVi banking demo app. Provides security auditing, route scaffolding, test running, and transaction analysis.

## Installation

```bash
claude --plugin-dir ./savi-banking-plugin
```

Or once published to a marketplace:
```bash
/plugin install savi-banking@your-marketplace
```

## Commands

| Command | Usage |
|---------|-------|
| `/savi-banking:security-audit` | OWASP Top 10 audit of the codebase |
| `/savi-banking:add-route [description]` | Scaffold a new Flask route + template |
| `/savi-banking:banking-test` | Run test suite and summarize results |

## Skills (auto-invoked)

| Skill | Triggers when |
|-------|--------------|
| `analyze-transactions` | User asks about spending, categories, cash flow |

## Hooks (automatic)

| Hook | Trigger | Effect |
|------|---------|--------|
| Block .env reads | Read tool on .env | Security — prevents secret leakage |
| Block dangerous bash | rm -rf, force push, reset --hard | Safety guard |
| Syntax check | Write/Edit on .py files | Catches errors immediately |

## MCP Servers

- **filesystem** — exposes the project directory for enhanced navigation
