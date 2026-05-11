# air

This repository provides Claude Code plugins and slash commands.

## Plugins

Plugins live in `.claude/plugins/`. Each plugin is a folder of reference documents that Claude reads when executing a related slash command.

### frontend-slides

Generates polished, self-contained HTML slide presentations.

**Slash command:** `/slides`

**Plugin files:**

| File | Purpose |
|------|---------|
| `html-template.md` | Base HTML structure, JS class architecture, inline editing, image pipeline |
| `STYLE_PRESETS.md` | 12 curated visual presets with exact colors, fonts, and signature elements |
| `viewport-base.css` | Mandatory base CSS — pasted verbatim into every generated presentation |
| `animation-patterns.md` | Entrance animations, background effects, and interactive patterns by vibe |

**Usage:** Run `/slides` to start an interactive session. Claude asks about your topic, audience, slide count, style, content, images, and editing preferences — then generates a single self-contained `presentation.html` file.

## Commands

Slash commands live in `.claude/commands/`. Each `.md` file becomes a `/command-name` you can invoke in any Claude Code session inside this repo.

| Command | Description |
|---------|-------------|
| `/slides` | Generate an HTML slide presentation |
