---
name: logbok
description: Use when user says /logbok or asks to analyze their daily activity log. Reads window-focus log from ~/lib/logbok/, produces a timetable with 15-minute increments, rich descriptions, and an Elon-style summary in plain text.
---

# Logbok Daily Activity Analysis

Analyze the window-focus log for a given day and produce a full timetable.

## Input

The skill accepts an optional date argument in `YYYYMMDD` format:
- `/logbok 20260515` — analyze May 15, 2026
- `/logbok` — analyze today (use `date +%Y%m%d` to get today's date)

## Step 1: Resolve date and run logbok

```bash
# If no date given, get today
DATE=$(date +%Y%m%d)
# If date given as arg, use it directly

python3 - ~/lib/logbok/$DATE << 'EOF'
import re, sys
from datetime import datetime
from zoneinfo import ZoneInfo
TZ = ZoneInfo("Europe/Warsaw")
for line in open(sys.argv[1]):
    parts = line.split(" ", 2)
    if len(parts) < 3: continue
    tstamp, proc, title = parts
    t = datetime.fromtimestamp(int(tstamp), tz=TZ).strftime("%H:%M:%S")
    proc = re.sub(r'.+/', '', proc)
    print(t, proc, title, end="")
EOF
```

The script outputs one line per ~60s sample, in Europe/Warsaw local time:
```
09:43:12 teams-for-linux (1) Chat | NG Common Standup | Microsoft Teams
09:44:05 teams-for-linux (1) Chat | NG Common Standup | Microsoft Teams
09:45:18 chrome Sprint 2026.4 — Planning Decision Report - Google Chrome
09:46:02 teams-for-linux (1) Chat | NG Common Standup | Microsoft Teams
...
```

Each line: `HH:MM:SS app window-title` — one sample per line, roughly one per minute.

## Step 2: Interpret the data

### App name mapping
- `teams-for-linux` → Microsoft Teams (note channel/DM name in title)
- `chrome` → Browser (note site/page in title)
- `mate-terminal` → Terminal (note task name if Claude Code task shown)
- `screen locked` → Screen locked (break/away)
- `jetbrains` / `idea` / `intellij` → IDE

### Teams title patterns
- `Chat | <Channel> | Microsoft Teams` → channel activity
- `Chat | <Name> | Microsoft Teams` → DM with person
- `Meeting compact view | <Meeting> | Microsoft Teams` → active meeting
- `(N) Chat | ...` → N unread notifications

### Terminal title patterns
- `✳ <task>` → Claude Code actively working on task
- `⠂ <task>` / `⠐ <task>` → Claude Code processing/thinking
- `maciej@pippin:~` → manual terminal work

### Sample interpretation
- Gap > 1 minute between samples = possible screen off / brief away
- Gap > 5 minutes = screen off or away
- Consecutive samples with `screen locked` = break
- Dominant app across a time range = primary activity
- Interleaved apps = context switching / parallel work

## Step 3: Produce the timetable

Output in **plain text**, no markdown headers or bullet symbols except dashes.

### Format rules
1. Skip empty slots (no activity) — show as a single gap line only if gap > 30 min
2. Collapse adjacent slots with same dominant activity into one block
3. Each block: time range + bold activity name + rich description
4. Rich description: what specifically happened (which channel, which Jira ticket, which MR, meeting topic, etc.)
5. Note context switches within a block if significant

### Template
```
────────────────────────────────────────────────────────────────
HH:MM – HH:MM  ACTIVITY NAME
────────────────────────────────────────────────────────────────
Rich description of what happened. Name specific channels, tickets,
people, URLs, tools. Note if activity was interrupted. Note notification
badges growing (indicates incoming messages). Distinguish DMs from
channel activity. For terminal: note what Claude Code was doing.

────────────────────────────────────────────────────────────────
HH:MM – HH:MM  SCREEN LOCKED (N min) — reason if obvious
────────────────────────────────────────────────────────────────
```

## Step 4: Elon-style summary

After the timetable, add a compact executive summary:

```
════════════════════════════════════════════════════════════════
   ELON-STYLE SUMMARY — MONTH DD, YYYY
════════════════════════════════════════════════════════════════

ACTIVE TIME: HH:MM–HH:MM (Xh Ymin total)
Screen locked: [list gaps with durations] = N min offline
EFFECTIVE DESK TIME: ~Xh

MEETINGS (~Xh total):
  – [list meetings with durations]

TOP CONTACTS (DMs):
  [ranked list with approx touch count]

DEEP WORK (~Xh total):
  [focused work blocks with durations]

RECURRING THREADS:
  [topics/channels revisited throughout the day with visit count]

DISTRACTIONS (~N min total):
  [YouTube, social media, personal browsing]

PERSONAL:
  [any personal tasks: travel booking, shopping, etc.]

DIAGNOSIS:
[2-3 sentences on productivity pattern, main friction, what got done]
```

The DIAGNOSIS (and the summary as a whole) must be sarcastic, cutting, and merciless — not polite or diplomatic.

**How to apply:** In the DIAGNOSIS and summary:
- Call out gaps between declared and actual productivity
- Name things plainly (3 standups = "standups as a lifestyle")
- Mock scope creep, open tasks with no progress, YouTube during work hours
- Claude Code tasks opened repeatedly without resolution — comment without mercy
- Personal errands during work hours — note them, with humor not judgment
- End sharp, brief, no softening
- Do NOT write: "commendable engagement", "solid work", "key achievements"

## Language

Write the timetable and summary in **English**. Window titles and app names stay in their original language.
