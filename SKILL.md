---
name: yougile
description: Yougile project management. Tasks, boards, columns, projects. Use when asked about Yougile tasks, boards, or project tracking.
---

# Yougile

Yougile REST API v2. Zero dependencies.

## Setup

If not configured yet, run onboarding:
```bash
python3 scripts/yg.py setup
```

## Quick Commands

```bash
YG="python3 ~/.claude/skills/yougile/scripts/yg.py"

$YG projects_list '{}'
$YG boards_list '{"projectId":"ID"}'
$YG columns_list '{"boardId":"ID"}'
$YG tasks_list '{"columnId":"ID"}'
$YG tasks_create '{"title":"Task","columnId":"ID"}'
$YG tasks_update '{"id":"ID","completed":true}'
$YG users_list '{}'
```

Descriptions use **HTML** (not Markdown!): `<b>`, `<i>`, `<br>`.
Use `checklists` for todo-lists inside tasks (not `subtasks` — those create separate board cards).
Rate limit: 50 req/min. Full docs: README.md
