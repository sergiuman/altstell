#!/bin/zsh
# AltStell 10-Day Autonomous Daily Restart & Graph Expansion Runner (macOS + Ollama + GitHub Pages)
set -e

export HOME="/Users/sergiuman"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

REPO_DIR="/Users/sergiuman/Desktop/Gemini/Books"
LOG_FILE="$REPO_DIR/logs/daily_evolution.log"
mkdir -p "$REPO_DIR/logs"

echo "============================================================" >> "$LOG_FILE"
echo "[AltStell Daily Runner] Started at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$LOG_FILE"

cd "$REPO_DIR"

# 1. Pull latest changes if remote exists
git pull --rebase origin main >> "$LOG_FILE" 2>&1 || true

# 2. Ensure local Ollama daemon is serving gemma2:latest
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  nohup /opt/homebrew/bin/ollama serve >/dev/null 2>&1 &
  sleep 4
fi

# 3. Execute Daily Graph Value Discovery + Principle Improvement + Video Synthesis + Git Push
/usr/bin/python3 "$REPO_DIR/engine/daily_self_improver.py" --publish >> "$LOG_FILE" 2>&1

# 4. Check if all 10 daily cycles have completed; if so, cleanly unload the launchd schedule
COMPLETED=$(/usr/bin/python3 -c "import json; d=json.load(open('$REPO_DIR/data/evolution_state.json')); print(d.get('completed_days', 0))" 2>/dev/null || echo "0")
MAX_DAYS=$(/usr/bin/python3 -c "import json; d=json.load(open('$REPO_DIR/data/evolution_state.json')); print(d.get('max_days', 10))" 2>/dev/null || echo "10")

echo "[AltStell Daily Runner] Progress: Day $COMPLETED / $MAX_DAYS" >> "$LOG_FILE"

if [ "$COMPLETED" -ge "$MAX_DAYS" ]; then
  echo "[AltStell Daily Runner] 10-Day Evolution Campaign complete!" >> "$LOG_FILE"
fi
