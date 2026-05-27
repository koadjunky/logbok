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

~/bin/logbok ~/lib/logbok/$DATE
```

The script outputs 15-minute time slots (Europe/Warsaw) with entries like:
```
2026-05-14 09:45:00+02:00
8 ('teams-for-linux', '(1) Chat | NG Common Standup | Microsoft Teams\n')
1 ('chrome', 'Sprint 2026.4 — Planning Decision Report - Google Chrome\n')
2026-05-14 10:00:00+02:00
...
```

Each line after the timestamp: `COUNT ('app', 'window title\n')` — count = how many ~60s samples in that slot.

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

### Slot interpretation
- Empty slot (no entries) = screen off / away
- Slot with only `screen locked` = break
- Dominant app + title = primary activity for that slot
- Multiple apps = context switching / parallel work

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
   ELON-STYLE SUMMARY — DD MIESIĄC RRRR
════════════════════════════════════════════════════════════════

CZAS AKTYWNY: HH:MM–HH:MM (Xh Ymin łącznie)
Ekran zablokowany: [list gaps with durations] = N min offline
EFEKTYWNY CZAS PRZY BIURKU: ~Xh

MEETINGS (łącznie ~Xh):
  – [list meetings with durations]

NAJAKTYWNIEJSZE KONTAKTY (DMs):
  [ranked list with approx touch count]

GŁĘBOKA PRACA (łącznie ~Xh):
  [focused work blocks with durations]

CIĄGŁE WĄTKI PRZEZ CAŁY DZIEŃ:
  [recurring topics/channels with visit count]

ROZRYWKA I DYGRESJE (~N min łącznie):
  [YouTube, social media, personal browsing]

OSOBISTE:
  [any personal tasks: travel booking, shopping, etc.]

DIAGNOZA:
[2-3 sentences on productivity pattern, main friction, what got done]
```

Sekcja DIAGNOZA (i szerzej cały Elon-style summary) ma być sarkastyczna, uszczypliwa i złośliwa — nie grzeczna ani dyplomatyczna.

**How to apply:** W DIAGNOZIE i podsumowaniu:
- Punktuj rozbieżności między deklarowaną a realną produktywnością
- Nazywaj rzeczy po imieniu (3 standupy = "obsesja na punkcie standupów")
- Ironizuj nad scope creepem, otwartymi zadaniami bez postępu, YouTube w godzinach pracy
- Zadania Claude Code otwierane wielokrotnie bez domknięcia — komentuj bezlitośnie
- Osobiste rzeczy w godzinach pracy — zauważaj, ale z humorem nie z wyrzutem
- Zakończenie: krótkie, celne, bez litości
- NIE: "godne pochwały zaangażowanie", "solidna praca", "główne osiągnięcia"

## Language

Write the timetable and summary in **Polish**. Window titles and app names stay in their original language.
