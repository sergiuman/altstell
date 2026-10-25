# ✦ AltStell — Alternative Storytelling · Stellar Minds (Age 11+)

**Live Interactive Platform:** **[https://sergiuman.github.io/altstell/](https://sergiuman.github.io/altstell/)**

> *Short-video interactive alternative storytelling powered by a Developmental Psychology Knowledge Graph & Autonomous Multi-Agent Engine — crafted specifically to grow 11-year-old minds in English & Romanian.*

---

## 🌟 Core Pillars

1. **TikTok-Velocity Attention · Zero-Harm Child Psychology**
   - Vertical `9:16` (`720×1280` H.264+AAC) snap-scroll short videos (`25` bilingual episodes = `50` web-optimized MP4s) with millisecond-locked 6-beat narration sync (`Samantha` EN / `Ioana` RO + `-23 dB` ambient bed).
   - **Alternative Storytelling Formats:** 3-second cognitive hooks, **Dual-Lens Perspective Flips** (System-1 reactive voice vs. growth voice), **Interactive Branching Dilemmas** (*"What Would You Do?"* with zero-shame natural consequences), **Somatic Mindful Cues**, and **2-Minute Offline Real-World Quests**.
   - **Anti-Doomscroll Screen Guard:** Gentle mindful check-in every 6 shorts encouraging offline transfer and eye/posture rest.

2. **Consolidated 17-Book Bilingual Library (Age 11 Edition — EN & RO)**
   - Complete middle-grade narrative adaptations (Markdown + compiled PDFs + in-app chapter reader with instant search) of 17 foundational books:
     1. *The Whispering Forest / Lumea prin ochii lui Radu* (Peter Senge — *The Fifth Discipline*)
     2. *Seven Paths of Eldoria / Ileana și cele șapte turnuri* (Stephen Covey — *The 7 Habits*)
     3. *Chronicles of the Forest / NOI: Povestea oamenilor* (Yuval Noah Harari — *Sapiens*)
     4. *Whisperers of Eldoria / Doar un pic mai aproape* (Charles Duhigg — *Supercommunicators*)
     5. *Sparks of Eldoria / Doar un pic mai mult* (James Clear — *Atomic Habits*)
     6. *Heart Keepers of Eldoria / Doar un pic mai adânc* (Daniel Goleman — *Emotional Intelligence*)
     7. *Beyond the Whispering Valley / Doar un pic mai puțin haos* (Jordan Peterson — *Beyond Order*)
     8. *The Garden of Growth / Grădina Dezvoltării* (Carol Dweck — *Mindset*)
     9. *The Mountain of the Slow Climber / Muntele Urcușului Răbdător* (Angela Duckworth — *Grit*)
     10. *The Island of the Quiet Forge / Insula Faurului Liniștit* (Cal Newport — *Deep Work*)
     11. *The Hare and the Owl of the Mind / Iepurele și Bufnița Minții* (Daniel Kahneman — *Thinking, Fast and Slow*)
     12. *The Whispering Stream / Pârâul Șoptitor* (Susan Cain — *Quiet*)
     13. *The Path in the Snow / Drumul prin zăpadă* (Charlie Mackesy — *The Boy, the Mole, the Fox and the Horse*)
     14. *The Secret of the Lighthouse / Secretul Farului din Poiană* (Simon Sinek — *Start With Why*)
     15. *The Night-Garden of Dreams / Grădina de Noapte a Viselor* (Matthew Walker — *Why We Sleep*)
     16. *The Iron Pebble / Pietricica de Fier* (David Goggins — *Can't Hurt Me*, child-psychologist adaptation)
     17. *The Glass Mirror and the Muddy Trail / Oglinda de Sticlă și Cărarea cu Noroi* (Jonathan Haidt — *The Anxious Generation*)

3. **Dual Graph Architecture (`NetworkX` + Local `Ollama gemma2:latest`)**
   - **Psychological Value Knowledge Graph (`data/knowledge_graph.json`):** `87` nodes (`17` Books, `28` Developmental Values, `17` 11yo Dilemmas, `25` Short-Video Episodes) and `274` weighted edges (`TEACHES_VALUE`, `SYNERGIZES_WITH`, `CONTRASTS_TENSION`, `SOLVES_DILEMMA`, `DRAMATIZES_BOOK`, `ACTIVATE_VALUE`, `NEXT_SPARK`) with weighted PageRank centrality and interactive Canvas Constellation exploration.
   - **7-Node Multi-Agent Execution StateGraph (`engine/daily_self_improver.py`):**
     `CuratorNode → PrincipleImproverNode → ValueBridgeSelectorNode → AltStoryArchitectNode ⇄ ChildPsychGuardNode → MediaStudioNode → GraphSyncAndPublishNode`

4. **10 Verified QA Sessions (`64.55` → `99.46 / 100`) & 10-Day Auto-Evolution**
   - Full telemetry recorded in [`qa/QA_10_SESSIONS_REPORT.md`](qa/QA_10_SESSIONS_REPORT.md) and [`qa/qa_sessions_history.json`](qa/qa_sessions_history.json) with **10/10 strictly positive measured increments**.
   - Automated daily execution for the next 10 days via macOS `launchd` (`com.altstell.daily.evolution` running `engine/run_daily_daemon.sh` with local `Ollama gemma2:latest` + auto-push to GitHub Pages) and `.github/workflows/daily_graph_evolution.yml`.
