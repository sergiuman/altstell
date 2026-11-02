#!/usr/bin/env python3
"""
Persistent Local OS Scheduler Daemon for AltStell's 10-Day Autonomous Evolution.

Runs directly on macOS in the background (without requiring ~/Library/LaunchAgents):
1. Catches up any missed calendar days since campaign start (e.g. if the Mac was asleep).
2. Automatically executes `engine/run_daily_daemon.sh` once per calendar day after 09:00 local time
   until `completed_days >= max_days`, pushing every new episode & principle to GitHub Pages.
"""
import json
import os
import subprocess
import time
from datetime import datetime, timezone

BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
STATE_PATH = os.path.join(BASE_DIR, "data", "evolution_state.json")
RUNNER_SH = os.path.join(BASE_DIR, "engine", "run_daily_daemon.sh")
LOG_DIR = os.path.join(BASE_DIR, "logs")


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_days": 0, "max_days": 11, "started_at": "2026-10-25T22:03:46+00:00"}


def target_days_by_today(state) -> int:
    started_str = state.get("started_at", "2026-10-25T22:03:46+00:00")
    try:
        start_dt = datetime.fromisoformat(started_str.replace("Z", "+00:00")).astimezone()
    except Exception:
        start_dt = datetime(2026, 10, 25, tzinfo=timezone.utc).astimezone()
    now_local = datetime.now().astimezone()
    calendar_diff = (now_local.date() - start_dt.date()).days
    # Day 1 ran on Oct 25; each new calendar day after 09:00 adds +1 target run up to max_days
    extra = 1 if now_local.hour >= 9 else 0
    desired = max(1, calendar_diff + extra)
    return min(int(state.get("max_days", 11)), desired)


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    daemon_log = os.path.join(LOG_DIR, "autonomous_loop.log")
    while True:
        state = load_state()
        completed = int(state.get("completed_days", 0))
        max_days = int(state.get("max_days", 11))
        if completed >= max_days:
            with open(daemon_log, "a", encoding="utf-8") as lf:
                lf.write(f"[{datetime.now().isoformat()}] Campaign complete ({completed}/{max_days}). Exiting.\n")
            break

        target = target_days_by_today(state)
        if completed < target:
            with open(daemon_log, "a", encoding="utf-8") as lf:
                lf.write(f"[{datetime.now().isoformat()}] Running cycle {completed + 1}/{max_days} (target today: {target})...\n")
            subprocess.run(["/bin/zsh", RUNNER_SH], cwd=BASE_DIR, check=False)
            time.sleep(5)
            continue

        time.sleep(1800)


if __name__ == "__main__":
    main()
