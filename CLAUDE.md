# logbok — Claude Code context

Personal window-focus time tracker. Three independent components sharing a log format.

## Log format

Raw logs live in `~/lib/logbok/YYYYMMDD`, one line per ~60s cron sample:

```
1716890592 /usr/bin/teams-for-linux Chat | NG Common Standup | Microsoft Teams
1716890712 screen screen locked
```

Fields: `epoch_timestamp process_path window_title`. Process path is always the full path from `ps`; window title is free-form text from `xdotool`.

## Components

### `scripts/logbok.record`
Bash cron script. No dependencies beyond `xdotool` and `mate-screensaver-command`. Writes to `~/lib/logbok/YYYYMMDD`. Do not touch unless fixing recorder behavior.

### `logbok` + `logbok.py`
Human-readable viewer. `logbok` is a bash wrapper that activates `~/lib/logbok.venv` and runs `~/lib/logbok.py`. `logbok.py` uses `pendulum` (requires the venv). Aggregates into 15-min buckets. These files are deployed manually — `logbok` to `~/bin/`, `logbok.py` to `~/lib/`.

### `skills/logbok/SKILL.md`
Claude Code skill. **Self-contained** — Python stdlib only (`datetime`, `zoneinfo`, `re`), no venv. The inline Python script converts epoch → `HH:MM:SS` (Europe/Warsaw) and strips the process path prefix. Claude then does all grouping and analysis.

## Plugin versioning

Two files must stay in sync — bump both together:
- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Plugin is published at `https://github.com/koadjunky/logbok.git`. After bumping version, commit and push — users pick it up via `/plugin marketplace update koadjunky-logbok-skill`.

## Installed skill locations

The skill is loaded from the marketplace cache, not from personal-skills. After editing `skills/logbok/SKILL.md`, sync manually if testing locally before pushing:

```bash
cp skills/logbok/SKILL.md ~/.claude/plugins/marketplaces/koadjunky-logbok-skill/skills/logbok/SKILL.md
```

## What NOT to do

- Do not add dependencies to the skill — it must stay stdlib-only.
- Do not modify `logbok.py` to change the AI analysis format — that logic lives in SKILL.md.
- Do not merge `logbok.py` and `logbok_ai.py` concerns — the venv viewer and the skill serve different purposes.
- The `logbok` wrapper hardcodes `~/lib/logbok.venv` and `~/lib/logbok.py` — do not change those paths without updating the wrapper.
