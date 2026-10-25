#!/usr/bin/env python3
"""
AltStell 10-Day Autonomous Graph Self-Improvement & Content Expansion Workflow.

Runs on macOS using local Ollama (gemma2:latest) + NetworkX Multi-Agent Execution Graph + FFmpeg + GitHub CLI.
Designed to restart automatically each day for 10 days (via launchd + cron schedule), each day:
1. Learning from current graph centrality & QA metrics to refine `data/storytelling_principles.json`.
2. Discovering the highest-potential unbridged pair of psychological values in `data/knowledge_graph.json`.
3. Generating a brand-new bilingual (EN + RO) 11-year-old Alternative Storytelling episode via local Ollama gemma2.
4. Auditing & iteratively revising through the ChildPsychGuardNode conditional graph loop.
5. Synthesizing 9:16 vertical MP4 short videos (EN + RO) with subpixel motion, captions, and voiceover.
6. Updating the Knowledge Graph & web feed, validating via QA Engine, and auto-pushing to GitHub Pages!
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine import ollama_client
from engine.graph_engine import (
    DEFAULT_PRINCIPLES,
    FEED_PATH,
    GRAPH_PATH,
    PRINCIPLES_PATH,
    AgentExecutionGraph,
    KnowledgeGraphManager,
)
from engine.render_short_videos import render_episode_video
from qa.qa_engine import flesch_kincaid_grade, HARM_SHAME_PATTERNS, BABY_TALK_PATTERNS

import re


EVOLUTION_STATE_PATH = os.path.join(BASE_DIR, "data", "evolution_state.json")
ACCENT_PALETTE = ["#38bdf8", "#a855f7", "#10b981", "#f59e0b", "#ec4899", "#6366f1", "#14b8a6"]
ALT_FORMATS = ["PERSPECTIVE_FLIP", "BRANCHING_CHOICE", "RIPPLE_TIMELINE", "BRAIN_GLITCH", "QUIET_SPARK"]


def load_evolution_state() -> Dict[str, Any]:
    if os.path.exists(EVOLUTION_STATE_PATH):
        with open(EVOLUTION_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "campaign_name": "AltStell 10-Day Autonomous Graph Evolution",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_days": 0,
        "max_days": 10,
        "ollama_model": ollama_client.DEFAULT_MODEL,
        "daily_runs": [],
    }


def save_evolution_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(EVOLUTION_STATE_PATH), exist_ok=True)
    with open(EVOLUTION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def build_daily_agent_graph(render_media: bool = True, publish_git: bool = False) -> AgentExecutionGraph:
    g = AgentExecutionGraph()

    def curator_node(state: Dict[str, Any]) -> Dict[str, Any]:
        kg = KnowledgeGraphManager(GRAPH_PATH)
        kg.load()
        with open(FEED_PATH, "r", encoding="utf-8") as f:
            feed_doc = json.load(f)
        episodes = feed_doc.get("episodes", [])
        kg.sync_episodes_into_graph(episodes)
        metrics = kg.compute_graph_metrics()

        if os.path.exists(PRINCIPLES_PATH):
            with open(PRINCIPLES_PATH, "r", encoding="utf-8") as f:
                principles = json.load(f)
        else:
            principles = dict(DEFAULT_PRINCIPLES)

        state["kg"] = kg
        state["feed_doc"] = feed_doc
        state["episodes"] = episodes
        state["graph_metrics"] = metrics
        state["principles"] = principles
        state["revision_attempts"] = 0
        return state

    def principle_improver_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Uses Ollama gemma2 to evolve the storytelling principles based on current graph values."""
        principles = state["principles"]
        metrics = state["graph_metrics"]
        top_vals = ", ".join(v["label_en"] for v in metrics.get("top_central_values", [])[:4])

        prompt = (
            f"Current AltStell Storytelling Principles (v{principles.get('version', 1)}) for 11-year-olds:\n"
            + "\n".join(f"- {h}" for h in principles.get("learned_heuristics", [])[-4:])
            + f"\nMost central values in our Knowledge Graph right now: {top_vals}.\n"
            "Formulate ONE sharp, actionable new child-psychology storytelling heuristic (1 sentence, <28 words) "
            "that makes 45-second interactive stories even more transformative and non-addictive for 11-year-olds.\n"
            'Respond in JSON: {"new_heuristic": "..."}'
        )
        res = ollama_client.generate_json(
            prompt=prompt,
            system="You are a Developmental Child Psychologist refining an ethical Alternative Storytelling engine.",
            temperature=0.45,
            max_tokens=180,
        )
        new_h = (res or {}).get("new_heuristic", "").strip()
        if not new_h or len(new_h) < 15:
            new_h = (
                f"Anchor abstract values ({top_vals}) inside concrete 11-year-old peer moments where pausing 3 seconds changes the outcome."
            )
        if new_h not in principles.setdefault("learned_heuristics", []):
            principles["learned_heuristics"].append(new_h)
            principles["version"] = int(principles.get("version", 1)) + 1
            principles["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(PRINCIPLES_PATH, "w", encoding="utf-8") as f:
                json.dump(principles, f, ensure_ascii=False, indent=2)

        state["new_principle_heuristic"] = new_h
        return state

    def value_bridge_selector_node(state: Dict[str, Any]) -> Dict[str, Any]:
        kg: KnowledgeGraphManager = state["kg"]
        bridge = kg.discover_next_value_bridge(state["episodes"])
        va_node = kg.G.nodes.get(bridge["value_a"], {})
        vb_node = kg.G.nodes.get(bridge["value_b"], {})
        bridge["label_a_en"] = va_node.get("label_en", bridge["value_a"])
        bridge["label_b_en"] = vb_node.get("label_b_en") or vb_node.get("label_en", bridge["value_b"])
        bridge["label_a_ro"] = va_node.get("label_ro", bridge["value_a"])
        bridge["label_b_ro"] = bridge.get("label_b_ro") or vb_node.get("label_ro", bridge["value_b"])
        state["selected_bridge"] = bridge
        return state

    def altstory_architect_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a complete bilingual 11yo Alternative Storytelling episode via local Ollama gemma2."""
        bridge = state["selected_bridge"]
        episodes = state["episodes"]
        next_num = len(episodes) + 1
        ep_id = f"ep_{next_num:02d}"
        alt_fmt = ALT_FORMATS[next_num % len(ALT_FORMATS)]
        accent = ACCENT_PALETTE[next_num % len(ACCENT_PALETTE)]
        critique = state.get("guard_critique", "")

        story_seed = bridge.get("story_seed_en", "")
        prompt = f"""Create a new bilingual (English + Romanian with full diacritics ă, â, î, ș, ț) short-video episode for 11-year-olds (6th grade).
Combine these two Knowledge Graph values:
- Value A: {bridge['label_a_en']} ({bridge['label_a_ro']})
- Value B: {bridge['label_b_en']} ({bridge['label_b_ro']})
Emergent Principle: {bridge.get('emergent_principle_en', '')}
{f'Narrative Seed to dramatize: {story_seed}' if story_seed else ''}
Storytelling Principle to honor: {state.get('new_principle_heuristic', '')}
STRICT AGE-11 RULE: Write for smart 11-year-olds (Flesch-Kincaid Grade 5.5-7.0, 18-23 words per beat). NEVER use preschool tropes like 'took his toy' or 'cookie jar'; use authentic 6th-grade moments (lockers, science lab, sports, friend misunderstandings, music, coding).
{f'Fix this QA critique from previous draft: {critique}' if critique else ''}

Return ONLY valid JSON with this exact structure:
{{
  "title": {{"en": "Catchy 4-7 word title", "ro": "Titlu captivant 4-7 cuvinte cu diacritice"}},
  "hook": {{"en": "Surprising 12-18 word 3-second cognitive hook for an 11-year-old", "ro": "Cârlig cognitiv de 12-18 cuvinte cu diacritice"}},
  "beats": [
    {{"beat_index": 1, "visual_cue": "hook_zoom", "caption_en": "18-22 vivid words...", "caption_ro": "18-22 cuvinte vii cu diacritice..."}},
    {{"beat_index": 2, "visual_cue": "tension_pan", "caption_en": "18-22 vivid words...", "caption_ro": "18-22 cuvinte..."}},
    {{"beat_index": 3, "visual_cue": "inner_voice", "caption_en": "18-22 vivid words...", "caption_ro": "18-22 cuvinte..."}},
    {{"beat_index": 4, "visual_cue": "shift_moment", "caption_en": "18-22 vivid words...", "caption_ro": "18-22 cuvinte..."}},
    {{"beat_index": 5, "visual_cue": "action_ripple", "caption_en": "18-22 vivid words...", "caption_ro": "18-22 cuvinte..."}},
    {{"beat_index": 6, "visual_cue": "constellation_close", "caption_en": "18-22 vivid words...", "caption_ro": "18-22 cuvinte..."}}
  ],
  "perspective_flip": {{
    "lens_a_label": {{"en": "Impulse Lens", "ro": "Lentila Impulsului"}},
    "lens_a_thought": {{"en": "22-30 words reactive inner voice...", "ro": "22-30 cuvinte voce reactivă..."}},
    "lens_b_label": {{"en": "Constellation Lens", "ro": "Lentila Înțelepciunii"}},
    "lens_b_thought": {{"en": "22-30 words growth inner voice...", "ro": "22-30 cuvinte voce matură..."}}
  }},
  "interactive_dilemma": {{
    "situation": {{"en": "Realistic 11yo school/friend dilemma...", "ro": "Dilemă realistă la 11 ani..."}},
    "choice_a": {{"label": {{"en": "Reactive move", "ro": "Mișcarea impulsivă"}}, "ripple": {{"en": "15-24 words constructive explanation of what happens...", "ro": "15-24 cuvinte explicație caldă..."}}, "is_growth_choice": false}},
    "choice_b": {{"label": {{"en": "Wise fusion move", "ro": "Mișcarea înțeleaptă"}}, "ripple": {{"en": "15-24 words empowering outcome...", "ro": "15-24 cuvinte rezultat pozitiv..."}}, "is_growth_choice": true}},
    "psych_takeaway": {{"en": "One crisp psychological truth for 11-year-olds.", "ro": "Un adevăr psihologic clar pentru 11 ani."}}
  }},
  "mindful_cue": {{"en": "Take one slow breath and notice your shoulders drop.", "ro": "Inspiră lent o dată și simte cum ți se relaxează umerii."}},
  "offline_quest": {{
    "title": {{"en": "2-Minute Real-World Spark", "ro": "Scânteia de 2 Minute în Viața Reală"}},
    "instruction": {{"en": "Concrete 2-minute offline action an 11yo can try today.", "ro": "Acțiune concretă offline de 2 minute azi."}}
  }}
}}"""

        draft = ollama_client.generate_json(
            prompt=prompt,
            system="You are AltStell's Lead Child-Psychologist Storyteller writing middle-grade (age 11) bilingual stories.",
            temperature=0.55,
            max_tokens=2000,
        )

        la_en, lb_en = bridge["label_a_en"], bridge["label_b_en"]
        la_ro, lb_ro = bridge["label_a_ro"], bridge["label_b_ro"]

        if not draft or not isinstance(draft.get("beats"), list) or len(draft.get("beats", [])) < 6:
            # High-craft deterministic synthesis if LLM JSON truncated
            draft = {
                "title": {
                    "en": f"When {la_en} Meets {lb_en}",
                    "ro": f"Când {la_ro} întâlnește {lb_ro}",
                },
                "hook": {
                    "en": f"What happens when you combine {la_en.lower()} with {lb_en.lower()} right when everyone else panics?",
                    "ro": f"Ce se întâmplă când îmbini {la_ro.lower()} cu {lb_ro.lower()} chiar când toți ceilalți intră în panică?",
                },
                "beats": [
                    {"beat_index": 1, "visual_cue": "hook_zoom", "caption_en": f"During sixth-period science lab, our bridge model cracked five minutes before judging, and my teammates started blaming each other loudly.", "caption_ro": f"La laboratorul de științe, macheta podului nostru a crăpat cu cinci minute înainte de jurizare, iar colegii au început să se certe."},
                    {"beat_index": 2, "visual_cue": "tension_pan", "caption_en": f"My first instinct was either to argue back or quit on the spot because the mistake felt embarrassing.", "caption_ro": f"Primul meu instinct a fost fie să mă cert și eu, fie să renunț pe loc, fiindcă greșeala părea rușinoasă."},
                    {"beat_index": 3, "visual_cue": "inner_voice", "caption_en": f"Then I practiced {la_en}: I paused for three calm seconds to spot where the real pressure point actually sat.", "caption_ro": f"Apoi am activat {la_ro}: m-am oprit trei secunde în liniște ca să văd unde era adevăratul punct de presiune."},
                    {"beat_index": 4, "visual_cue": "shift_moment", "caption_en": f"Next came {lb_en}: instead of rushing a messy patch, we reinforced one small support beam together with steady focus.", "caption_ro": f"A urmat {lb_ro}: în loc să cârpim totul în grabă, am întărit împreună o singură grindă de sprijin cu atenție."},
                    {"beat_index": 5, "visual_cue": "action_ripple", "caption_en": f"Our bridge held the full weight test—not because nothing broke, but because two quiet skills worked together.", "caption_ro": f"Podul nostru a rezistat testului complet—nu fiindcă nu s-a rupt nimic, ci fiindcă două puteri liniștite au lucrat împreună."},
                    {"beat_index": 6, "visual_cue": "constellation_close", "caption_en": f"One skill notices the hidden pattern; the second turns that insight into steady, courageous action.", "caption_ro": f"O abilitate observă tiparul ascuns, iar a doua transformă acea descoperire în acțiune calmă și curajoasă."},
                ],
                "perspective_flip": {
                    "lens_a_label": {"en": "Panic Reflex", "ro": "Reflexul de Panică"},
                    "lens_a_thought": {"en": "Everything is ruined, everyone is watching, and someone needs to take the blame for this broken project right now!", "ro": "Totul e stricat, toată clasa se uită la noi și cineva trebuie să fie de vină chiar acum!"},
                    "lens_b_label": {"en": f"{la_en} + {lb_en}", "ro": f"{la_ro} + {lb_ro}"},
                    "lens_b_thought": {"en": "A crack is just information showing us where the structure needs support. Pause, see the pattern, and fix one beam together.", "ro": "O crăpătură este doar o informație care ne arată unde e nevoie de sprijin. Respirăm, vedem tiparul și reparăm împreună."},
                },
                "interactive_dilemma": {
                    "situation": {"en": "Your group project glitches right before class presentation and two friends start arguing.", "ro": "Proiectul echipei voastre se strică fix înainte de prezentare, iar doi colegi încep să se certe."},
                    "choice_a": {
                        "label": {"en": "Join the blame argument", "ro": "Intri în cearta vinovăției"},
                        "ripple": {"en": "The clock runs out while everyone defends their ego, leaving the real problem untouched and stress sky-high.", "ro": "Timpul expiră în timp ce fiecare își apără orgoliul, lăsând problema nerezolvată și stresul la maximum."},
                        "is_growth_choice": False,
                    },
                    "choice_b": {
                        "label": {"en": "Pause & fix one key piece", "ro": "Oprește-te și repară piesa-cheie"},
                        "ripple": {"en": "Your calm focus lowers everyone's stress and rallies the team around the one fix that actually matters.", "ro": "Calmul tău scade tensiunea grupului și adună echipa în jurul singurei reparații care contează cu adevărat."},
                        "is_growth_choice": True,
                    },
                    "psych_takeaway": {
                        "en": f"Pairing {la_en} with {lb_en} turns group panic into calm leadership.",
                        "ro": f"Îmbinarea dintre {la_ro} și {lb_ro} transformă panica de grup în leadership calm.",
                    },
                },
                "mindful_cue": {
                    "en": "Drop your shoulders, inhale for 4 counts, and name one small thing you can control right now.",
                    "ro": "Relaxează umerii, inspiră numărând până la 4 și alege un singur lucru mic pe care îl poți controla acum.",
                },
                "offline_quest": {
                    "title": {"en": "The 2-Minute Pattern Spotter", "ro": "Detectivul de Tipare (2 Minute)"},
                    "instruction": {"en": "Step away from screens, pick one tricky homework or room mess, find the single root bottleneck, and fix just that piece.", "ro": "Lasă ecranul două minute, alege o temă grea sau un colț dezordonat, găsește cauza principală și rezolvă doar acel pas."},
                },
            }

        draft.setdefault("mindful_cue", {
            "en": "Drop your shoulders, inhale for 4 counts, and name one small choice you control right now.",
            "ro": "Relaxează umerii, inspiră numărând până la 4 și alege un singur pas pe care îl poți controla acum.",
        })

        episode_obj = {
            "id": ep_id,
            "order": next_num,
            "is_graph_fusion": True,
            "generated_by": f"ollama:{ollama_client.DEFAULT_MODEL}+graph_bridge",
            "bridge_id": bridge.get("bridge_id", ""),
            "book_ids": list(dict.fromkeys([bridge.get("book_a", "book_01"), bridge.get("book_b", "book_08")])),
            "value_ids": [bridge["value_a"], bridge["value_b"]],
            "dilemma_id": "dil_01",
            "category": "graph_fusion",
            "alt_format": alt_fmt,
            "art_theme": "campfire_myth",
            "accent_color": accent,
            "duration_target_sec": 45,
            **draft,
            "beats": draft["beats"][:6],
        }
        state["candidate_episode"] = episode_obj
        state["revision_attempts"] = state.get("revision_attempts", 0) + 1
        return state

    def child_psych_guard_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Audits the candidate episode for 11yo readability, zero harm, diacritics, and completeness."""
        ep = state["candidate_episode"]
        en_txt = ep["hook"]["en"] + " " + " ".join(b.get("caption_en", "") for b in ep["beats"])
        ro_txt = ep["hook"]["ro"] + " " + " ".join(b.get("caption_ro", "") for b in ep["beats"])

        fk = flesch_kincaid_grade(en_txt)
        harm = sum(1 for p in HARM_SHAME_PATTERNS + BABY_TALK_PATTERNS if re.search(p, en_txt, re.I))
        ro_diacritics = sum(1 for c in ro_txt if c in "ăâîșțĂÂÎȘȚ")

        preschool_hits = sum(1 for p in [r"\btoy\b", r"\bcookie jar\b", r"\bmommy\b", r"\bdaddy\b"] if re.search(p, en_txt, re.I))
        score = 100.0
        reasons = []
        if harm > 0:
            score -= 40.0
            reasons.append("Remove any shaming or baby-talk language.")
        if preschool_hits > 0:
            score -= 18.0
            reasons.append("Replace preschool tropes ('toy', 'cookie jar') with authentic 6th-grade 11yo school/friend moments.")
        if fk < 4.8 or fk > 8.2:
            score -= 14.0
            reasons.append(f"Adjust English readability from FK {fk:.1f} into middle-grade 5.2–7.5 range (18-23 words per beat).")
        if ro_diacritics < 8:
            score -= 20.0
            reasons.append("Ensure authentic Romanian diacritics (ă, â, î, ș, ț) throughout all Romanian fields.")
        if len(ep.get("beats", [])) != 6:
            score -= 25.0
            reasons.append("Provide exactly 6 story beats.")

        state["guard_score"] = score
        state["guard_critique"] = " ".join(reasons)
        return state

    def guard_router(state: Dict[str, Any]) -> str:
        if state.get("guard_score", 0) >= 95.0 or state.get("revision_attempts", 0) >= 2:
            return "MediaStudioNode"
        return "AltStoryArchitectNode"

    def media_studio_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ep = state["candidate_episode"]
        eid = ep["id"]
        ep["video_en"] = f"assets/videos/{eid}_en.mp4"
        ep["video_ro"] = f"assets/videos/{eid}_ro.mp4"
        ep["poster"] = f"assets/thumbs/{eid}.jpg"

        if render_media:
            res_en = render_episode_video(ep, "en", force=True)
            res_ro = render_episode_video(ep, "ro", force=True)
            ep["duration_en_sec"] = res_en.get("duration_sec", 44.0)
            ep["duration_ro_sec"] = res_ro.get("duration_sec", 46.0)
            # Compute cumulative beat start timestamps for synced interactive UI
            for lang_key, res_obj in [("en", res_en), ("ro", res_ro)]:
                bdurs = res_obj.get("beat_durations", [7.0] * 6)
                starts = []
                acc = 0.0
                for d in bdurs:
                    starts.append(round(acc, 2))
                    acc += d
                ep[f"beat_timestamps_{lang_key}"] = starts
        return state

    def graph_sync_and_publish_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ep = state["candidate_episode"]
        episodes: List[Dict[str, Any]] = state["episodes"]
        episodes.append(ep)

        feed_doc = state["feed_doc"]
        feed_doc["episodes"] = episodes
        feed_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
        feed_doc["total_episodes"] = len(episodes)
        with open(FEED_PATH, "w", encoding="utf-8") as f:
            json.dump(feed_doc, f, ensure_ascii=False, indent=2)

        kg: KnowledgeGraphManager = state["kg"]
        bridge = state["selected_bridge"]
        kg.raw_data.setdefault("edges", []).append({
            "source": bridge["value_a"],
            "target": bridge["value_b"],
            "relation": "SYNERGIZES_WITH",
            "weight": 0.94,
            "learned_by_workflow": True,
            "episode_id": ep["id"],
        })
        kg.sync_episodes_into_graph(episodes)
        new_metrics = kg.compute_graph_metrics()
        kg.save()
        state["updated_graph_metrics"] = new_metrics

        if publish_git:
            try:
                subprocess.run(["git", "add", "data/", "assets/videos/", "assets/thumbs/", "qa/"], cwd=BASE_DIR, check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"feat(evolution): autonomous daily graph episode {ep['id']} ({ep['title']['en']})"],
                    cwd=BASE_DIR,
                    check=False,
                )
                subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=False)
                state["git_published"] = True
            except Exception as exc:
                state["git_published"] = False
                state["git_error"] = str(exc)

        return state

    g.add_agent_node("CuratorNode", curator_node)
    g.add_agent_node("PrincipleImproverNode", principle_improver_node)
    g.add_agent_node("ValueBridgeSelectorNode", value_bridge_selector_node)
    g.add_agent_node("AltStoryArchitectNode", altstory_architect_node)
    g.add_agent_node("ChildPsychGuardNode", child_psych_guard_node)
    g.add_agent_node("MediaStudioNode", media_studio_node)
    g.add_agent_node("GraphSyncAndPublishNode", graph_sync_and_publish_node)

    g.add_edge("CuratorNode", "PrincipleImproverNode")
    g.add_edge("PrincipleImproverNode", "ValueBridgeSelectorNode")
    g.add_edge("ValueBridgeSelectorNode", "AltStoryArchitectNode")
    g.add_edge("AltStoryArchitectNode", "ChildPsychGuardNode")
    g.add_conditional_edges("ChildPsychGuardNode", guard_router, ["MediaStudioNode", "AltStoryArchitectNode"])
    g.add_edge("MediaStudioNode", "GraphSyncAndPublishNode")

    return g


def run_daily_cycle(render_media: bool = True, publish_git: bool = False, force_run: bool = False) -> Dict[str, Any]:
    evo_state = load_evolution_state()
    if evo_state["completed_days"] >= evo_state["max_days"] and not force_run:
        print(f"[AltStell] 10-day evolution campaign already completed ({evo_state['completed_days']}/{evo_state['max_days']}).")
        return evo_state

    workflow = build_daily_agent_graph(render_media=render_media, publish_git=publish_git)
    result = workflow.run("CuratorNode", {})

    day_num = evo_state["completed_days"] + 1
    ep = result["candidate_episode"]
    evo_state["completed_days"] = day_num
    evo_state["last_run_at"] = datetime.now(timezone.utc).isoformat()
    evo_state["daily_runs"].append({
        "day": day_num,
        "timestamp": evo_state["last_run_at"],
        "episode_id": ep["id"],
        "title_en": ep["title"]["en"],
        "title_ro": ep["title"]["ro"],
        "bridged_values": ep["value_ids"],
        "guard_score": result.get("guard_score", 0),
        "new_principle": result.get("new_principle_heuristic", ""),
        "graph_nodes": result["updated_graph_metrics"]["total_nodes"],
        "graph_edges": result["updated_graph_metrics"]["total_edges"],
        "agent_trace": result.get("trace", []),
    })
    save_evolution_state(evo_state)
    print(f"[+] Completed Evolution Cycle Day {day_num}/{evo_state['max_days']} -> Generated {ep['id']}: {ep['title']['en']}")
    return evo_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AltStell Autonomous Graph Daily Evolution Cycle.")
    parser.add_argument("--no-media", action="store_true", help="Skip MP4 synthesis (dry test)")
    parser.add_argument("--publish", action="store_true", help="Auto-commit and git push to GitHub Pages")
    parser.add_argument("--force", action="store_true", help="Run even if 10-day counter reached")
    args = parser.parse_args()
    run_daily_cycle(render_media=not args.no_media, publish_git=args.publish, force_run=args.force)
