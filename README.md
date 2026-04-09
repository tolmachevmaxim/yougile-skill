# Yougile Skill for Claude Code & Codex

AI-native integration for [Yougile](https://yougile.com) project management. Zero dependencies — just Python 3.10+ and `urllib`.

Works with **Claude Code**, **Codex**, and **Cursor** as a self-configuring skill.

## Quick Start

### 1. Install

```bash
# Claude Code
git clone https://github.com/tolmachevmaxim/yougile-skill.git ~/.claude/skills/yougile

# Codex
git clone https://github.com/tolmachevmaxim/yougile-skill.git ~/.agents/skills/yougile

# Cursor
git clone https://github.com/tolmachevmaxim/yougile-skill.git ~/.cursor/skills/yougile
```

### 2. Setup

Just ask your AI assistant:

> "Connect to my Yougile account"

Or run manually:

```bash
python3 ~/.claude/skills/yougile/scripts/yg.py setup
```

The setup wizard will:
1. Ask for your Yougile email and password
2. Show your available companies
3. Create an API key
4. Store it securely (Keychain on macOS, Credential Manager on Windows, or env var)

> **Note:** If you registered via Google OAuth, set a password in [Yougile settings](https://yougile.com) first (Profile → Security → Set password).

### 3. Use

Ask your AI assistant naturally:

- "Show me all Yougile projects"
- "List tasks in the Development board"
- "Create a task 'Fix login bug' in the Backlog column"
- "Mark task PROJ-42 as completed"

## Manual Setup (without wizard)

If you prefer to configure manually:

### macOS (Keychain)
```bash
security add-generic-password -a $USER -s yougile-api-key -w 'YOUR_API_KEY'
```

### Windows (Credential Manager)
```cmd
cmdkey /generic:yougile-api-key /user:yougile /pass:YOUR_API_KEY
```

### Any OS (Environment Variable)
```bash
export YOUGILE_API_KEY='YOUR_API_KEY'
```

To get an API key, use the [Yougile API docs](https://ru.yougile.com/api-v2#/operations/createKey).

## All 28 Tools

| Tool | Description | Required Args |
|------|-------------|---------------|
| **setup** | Interactive onboarding wizard | — |
| **auth_companies** | List companies (login+password) | `login, password` |
| **auth_create_key** | Create API key | `login, password, companyId` |
| **auth_list_keys** | List API keys | `login, password` |
| **projects_list** | List projects | — |
| **projects_get** | Get project | `id` |
| **projects_create** | Create project | `title` |
| **projects_update** | Update project | `id` |
| **boards_list** | List boards | — |
| **boards_get** | Get board | `id` |
| **boards_create** | Create board | `title, projectId` |
| **boards_update** | Update board | `id` |
| **columns_list** | List columns | — |
| **columns_get** | Get column | `id` |
| **columns_create** | Create column | `title, boardId` |
| **columns_update** | Update column | `id` |
| **tasks_list** | List tasks (newest first) | — |
| **tasks_list_chrono** | List tasks (oldest first) | — |
| **tasks_get** | Get task | `id` |
| **tasks_create** | Create task | `title` |
| **tasks_update** | Update task | `id` |
| **users_list** | List users | — |
| **users_get** | Get user | `id` |
| **chat_messages** | Get chat messages | `chatId` |
| **chat_send** | Send chat message | `chatId, text, textHtml, label` |
| **webhooks_list** | List webhooks | — |
| **webhooks_create** | Create webhook | `url, event, filters` |
| **webhooks_update** | Update webhook | `id` |

## Usage Examples

```bash
YG="python3 ~/.claude/skills/yougile/scripts/yg.py"

# List all projects
$YG projects_list '{}'

# List boards in a project
$YG boards_list '{"projectId":"uuid-here"}'

# List columns on a board
$YG columns_list '{"boardId":"uuid-here"}'

# List tasks in a column
$YG tasks_list '{"columnId":"uuid-here"}'

# Create a task
$YG tasks_create '{"title":"Fix bug","columnId":"uuid-here","description":"Details..."}'

# Create task with deadline and assignee
$YG tasks_create '{"title":"Deploy v2","columnId":"uuid","assigned":["user-uuid"],"deadline":{"deadline":1714521600000}}'

# Complete a task
$YG tasks_update '{"id":"task-uuid","completed":true}'

# Move task to another column
$YG tasks_update '{"id":"task-uuid","columnId":"new-column-uuid"}'

# Search tasks by title
$YG tasks_list '{"title":"login"}'
```

## Yougile Hierarchy

```
Company
└── Project
    └── Board
        └── Column
            └── Task
                ├── Subtasks
                ├── Checklists
                ├── Chat messages
                └── Stickers (labels)
```

## API Notes

- **Rate limit:** 50 requests/minute per company
- **Max API keys:** 30 per company
- **Key expiry:** None (permanent until deleted)
- **Task filtering:** Use `columnId` or `assignedTo` (no `projectId` filter on tasks)
- **Deadlines:** Unix timestamps in milliseconds
- **Docs:** [ru.yougile.com/api-v2](https://ru.yougile.com/api-v2)

## Credential Lookup Order

1. Environment variable `YOUGILE_API_KEY`
2. macOS Keychain (`yougile-api-key`)
3. Windows Credential Manager (`yougile-api-key`)

## License

MIT
