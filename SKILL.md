---
name: yougile
description: Yougile project management. Tasks, boards, columns, projects. Use when asked about Yougile tasks, boards, or project tracking — to create a task, update a board, manage columns and projects.
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

Rate limit: 50 req/min. Full docs: references/api.md

## Task links

Direct link to task (full screen): `https://ru.yougile.com/team/messenger#CPO-38`
Get `idTaskProject` (e.g. `CPO-38`) from `tasks_get` response.

## Description Formatting (HTML only)

YouGile descriptions are **HTML, not Markdown**. The following rules are confirmed from real editor testing:

### What WORKS ✅

| Element | HTML |
|---------|------|
| Section header | `<h4><strong>Title</strong></h4>` |
| Bold | `<strong>text</strong>` |
| Italic | `<i>text</i>` |
| Bullet list | `<ul><li>item</li></ul>` |
| Nested list | `<ul><li>parent<ul><li>child</li></ul></li></ul>` |
| Empty line between sections | `<p> </p>` (non-breaking space inside) |
| Line break within paragraph | `<br>` |
| Paragraph | `<p>text</p>` |
| Link | `<a target="_blank" rel="noopener noreferrer" href="URL">text</a>` |
| Highlight/badge | `<span style="background-color:#B2D995">text</span>` |
| Checkbox (unchecked) | `<ul class="todo-list"><li><label class="todo-list__label"><input type="checkbox" disabled="disabled"><span class="todo-list__label__description">text</span></label></li></ul>` |
| Checkbox (checked) | same with `checked="checked"` on the input |

### What does NOT work ❌

- `<h1>`, `<h2>`, `<h3>` — use `<h4>` only
- Markdown syntax (`## Header`, `**bold**`, `- list`) — ignored
- Plain newlines `\n` — use `<br>` or `<p>` instead
- Markdown checkboxes `- [ ]` — use the todo-list HTML structure below
- `☐` unicode — renders as plain text, not an interactive checkbox

### Standard template for a structured ticket

Full HTML template: `references/ticket-template.html` (copy its contents into the `description` field).

Use `checklists` for todo-lists inside tasks (not `subtasks` — those create separate board cards).
