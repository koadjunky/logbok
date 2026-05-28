# logbok

Personal time tracker for Linux: records active window focus every minute and surfaces daily activity through a Claude Code AI skill.

## How it works

```
logbok.record (cron, every 60s)
  └─→ ~/lib/logbok/YYYYMMDD   (raw log: epoch + process + window title)
        ├─→ logbok / logbok.py  (human-readable 15-min bucket view)
        └─→ /logbok skill       (AI-powered timetable + summary)
```

## Components

### `scripts/logbok.record` — the recorder

Bash script meant to run as a cron job every minute. Captures:
- active window title (`xdotool`)
- process path (`ps`)
- current epoch timestamp

Detects screen lock via `mate-screensaver-command` and records a `screen locked` entry instead.

**Setup:**

```bash
# Install dependencies
sudo apt install xdotool mate-utils
```

Add to crontab (`crontab -e`):

```
* * * * * /path/to/logbok/scripts/logbok.record
```

Test manually before relying on cron — the script needs `DISPLAY=:0` and a running D-Bus session, both of which it sets automatically, but verify once:

```bash
bash /path/to/logbok/scripts/logbok.record
tail ~/lib/logbok/$(date +%Y%m%d)
```

**Limitations:**

- **X11 only** — uses `xdotool` which requires X11. Does not work under Wayland. The display is hardcoded to `:0`.
- **MATE desktop only** — screen lock detection uses `mate-screensaver-command`. On other desktop environments the script will always treat the screen as unlocked, logging whatever window happens to be active.
- **Single display** — only tracks the focused window on display `:0`. Multi-monitor setups with separate X screens are not supported.
- **Cron environment** — cron runs without a D-Bus session by default; the script works around this by hardcoding `unix:path=/run/user/1000/bus`, which assumes UID 1000.

Logs are written to `~/lib/logbok/YYYYMMDD`, one line per sample:

```
1716890592 /usr/bin/teams-for-linux Chat | NG Common Standup | Microsoft Teams
1716890652 /usr/bin/chrome logbok – SKILL.md · GitLab - Google Chrome
1716890712 screen locked
```

---

### `logbok` / `logbok.py` — human-readable viewer

Command-line viewer that aggregates raw samples into 15-minute buckets and counts app occurrences per slot. Requires a Python venv with `pendulum`.

**Setup:**

```bash
# Create the venv and install dependencies
python3 -m venv ~/lib/logbok.venv
~/lib/logbok.venv/bin/pip install -r requirements.txt

# Place files where the wrapper expects them
cp logbok.py ~/lib/logbok.py
cp logbok ~/bin/logbok
chmod +x ~/bin/logbok
```

The `logbok` wrapper activates `~/lib/logbok.venv` and runs `~/lib/logbok.py` — both paths are hardcoded in the script.

**Usage:**

```bash
# View a specific day
logbok ~/lib/logbok/20260528

# View today
logbok ~/lib/logbok/$(date +%Y%m%d)

# Page through output
logbok ~/lib/logbok/$(date +%Y%m%d) | less
```

**Output:**

```
2026-05-28 09:45:00+02:00
8 ('teams-for-linux', 'Chat | NG Common Standup | Microsoft Teams\n')
1 ('chrome', 'Sprint 2026.4 — Planning Decision Report\n')

2026-05-28 10:00:00+02:00
...
```

Each block is one 15-minute slot. The number before each entry is how many ~60s samples in that slot had that app+title as the active window.

---

### `skills/logbok/SKILL.md` — Claude Code AI skill

Reads the raw log for a given day and produces:
- a rich Polish-language timetable (collapsed by dominant activity)
- an Elon-style executive summary with productivity diagnosis

The skill is self-contained — no external scripts or venv required, Python stdlib only.

## Installing the skill

**One-liner:**

```bash
claude plugin marketplace add https://github.com/koadjunky/logbok.git && claude plugin install logbok
```

Or tell your Claude Code agent:

> Install the logbok skill from https://github.com/koadjunky/logbok.git

**Step by step:**

```bash
# Add the marketplace (once)
claude plugin marketplace add https://github.com/koadjunky/logbok.git

# Install the plugin
claude plugin install logbok
```

## Updating the skill

```
/plugin marketplace update koadjunky-logbok-skill
```

**Auto-update:** `/plugin` → Marketplaces → koadjunky-logbok-skill → Enable auto-update.

## Using the skill

```
/logbok              — analyze today
/logbok 20260515     — analyze May 15, 2026
```

## Repo structure

```
scripts/
  logbok.record       # cron recorder (bash, no dependencies)
logbok                # venv wrapper for logbok.py
logbok.py             # 15-min bucket viewer (requires pendulum venv)
requirements.txt      # Python dependencies for logbok.py
skills/
  logbok/
    SKILL.md          # Claude Code skill (self-contained, stdlib only)
.claude-plugin/
  plugin.json         # plugin manifest
  marketplace.json    # marketplace manifest
```

## Prerequisites

| Component | Requires |
|-----------|----------|
| `logbok.record` | `xdotool`, `mate-screensaver-command`, cron |
| `logbok.py` | Python 3.9+, `pendulum` (via venv) |
| `/logbok` skill | Claude Code, Python 3.9+ (stdlib only) |

The skill has no runtime dependencies beyond Python 3.9+ and Claude Code itself.

## License

Apache License 2.0
