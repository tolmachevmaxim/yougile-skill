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

Rate limit: 50 req/min. Full docs: README.md

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
| Checkbox (text) | `☐ item text` (unicode character, inside `<li>`) |

### What does NOT work ❌

- `<h1>`, `<h2>`, `<h3>` — use `<h4>` only
- Markdown syntax (`## Header`, `**bold**`, `- list`) — ignored
- Plain newlines `\n` — use `<br>` or `<p>` instead
- Markdown checkboxes `- [ ]` — use `☐` unicode character

### Standard template for a structured ticket

```html
<h4><strong>Goal (метрика)</strong></h4>
<ul>
<li>Главная: CR X → Y (+Z п.п.)</li>
<li>Вторичные: ...</li>
</ul>
<p>ICE: I=X, C=Y, E=Z → <strong>score</strong></p>
<p> </p>

<h4><strong>Segment</strong></h4>
<p>Кого задевает: seg1, seg2</p>
<ul><li>seg5 — описание;</li></ul>
<p>Job (JTBD): «...»</p>
<p> </p>

<h4><strong>Double Diamond</strong></h4>
<ul>
<li><strong>Problem hypothesis:</strong> ...</li>
<li><strong>Solution hypothesis:</strong> Если ..., то ..., потому что ...</li>
</ul>
<p> </p>

<h4><strong>Описание проблемы (As Is)</strong></h4>
<ul><li>...</li></ul>
<p> </p>

<h4><strong>Что нужно сделать (To Be)</strong></h4>
<ul>
<li>Шаг 1</li>
<li>Шаг 2<ul><li>Подшаг</li></ul></li>
</ul>
<p> </p>
<p><strong>Visual priority:</strong> 1. элемент 2. элемент</p>
<p> </p>

<h4><strong>Acceptance Criteria</strong></h4>
<ul>
<li>☐ критерий 1</li>
<li>☐ критерий 2</li>
</ul>
<p> </p>

<h4><strong>Analytics Requirements</strong></h4>
<ul>
<li>События:<ul>
<li><i>event_name</i>(param1, param2)</li>
</ul></li>
<li>Funnel: шаг1 → шаг2 → шаг3</li>
<li>Test vs Control: 50/50</li>
</ul>
<p> </p>

<h4><strong>References / Behavioral science</strong></h4>
<ul>
<li><strong>Principle:</strong> объяснение</li>
</ul>
<p> </p>

<h4><strong>Design</strong></h4>
<ul>
<li>Design needed: <strong>yes / no</strong></li>
<li>Figma link: <i>TBD</i></li>
</ul>
<p> </p>

<h4><strong>Временное ограничение</strong></h4>
<ul>
<li>Спринт: <strong>W17</strong></li>
<li>Причина: ...</li>
</ul>
<p> </p>

<h4><strong>Do not approve before test</strong></h4>
<ul>
<li>Test case: <i>TBD</i></li>
<li>Критерий успеха: ...</li>
</ul>
```

Use `checklists` for todo-lists inside tasks (not `subtasks` — those create separate board cards).
