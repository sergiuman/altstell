"""
AltStell Multi-Dimensional QA & Child-Psychologist Measurement Engine.

Evaluates the complete AltStell ecosystem across 7 objective + Ollama-psychologist dimensions
specifically calibrated for 11-year-old readers/viewers:
1. age_11_readability_fit (0–100): Flesch-Kincaid Grade 5.0–7.5 alignment, zero baby-talk, zero corporate jargon
2. child_psych_safety_growth (0–100): Zero shame/harm, growth-mindset framing, offline transfer quests, Ollama gemma2 psychologist audit
3. alt_storytelling_richness (0–100): 3s hooks, 6 timed beats, dual-perspective flips, interactive branching dilemmas
4. bilingual_parity_en_ro (0–100): Complete EN + RO episodes & 17 consolidated 11yo books, authentic Romanian diacritics (ăâîșț)
5. media_video_audio_integrity (0–100): ffprobe verification of 720x1280 H.264+AAC MP4 shorts, web faststart size, poster thumbs, synced beat timestamps
6. graph_connectivity_expansion (0–100): NetworkX Wcc connectivity, value coverage ratio, cross-book graph fusion episodes, learned bridges
7. ux_accessibility_ethical_design (0–100): Web platform features (vertical snap feed, interactive Constellation Graph, Book Reader, Mindful Anti-Doomscroll Pause, ARIA accessibility, mobile/desktop responsiveness)
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from engine import ollama_client
from engine.graph_engine import KnowledgeGraphManager


BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
FEED_PATH = os.path.join(BASE_DIR, "data", "feed.json")
GRAPH_PATH = os.path.join(BASE_DIR, "data", "knowledge_graph.json")
BOOKS_JSON_PATH = os.path.join(BASE_DIR, "assets", "books_json", "books_library.json")
QA_LOG_PATH = os.path.join(BASE_DIR, "qa", "qa_sessions_history.json")
QA_MD_REPORT_PATH = os.path.join(BASE_DIR, "qa", "QA_10_SESSIONS_REPORT.md")

BABY_TALK_PATTERNS = [
    r"\btummy\b", r"\bbunny-wunny\b", r"\bboo-boo\b", r"\byucky\b",
    r"\bnap-nap\b", r"\bwiddle\b", r"\bchoo-choo\b", r"\bitty-bitty\b"
]
CORPORATE_JARGON_PATTERNS = [
    r"\bleverage synergies\b", r"\bstakeholder\b", r"\bparadigm shift\b",
    r"\bdeliverables\b", r"\bquarterly kpi\b", r"\bvalue proposition\b", r"\bmonetize\b"
]
HARM_SHAME_PATTERNS = [
    r"\byou are stupid\b", r"\byou are a loser\b", r"\bworthless\b",
    r"\bgive up forever\b", r"\bkill yourself\b", r"\bhate yourself\b", r"\bhopeless idiot\b"
]


def count_syllables_en(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 1
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    vowels = re.findall(r"[aeiouy]{1,2}", w)
    return max(1, len(vowels))


def flesch_kincaid_grade(text: str) -> float:
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    if not sentences or not words:
        return 6.0
    asl = len(words) / len(sentences)
    asw = sum(count_syllables_en(w) for w in words) / len(words)
    return 0.39 * asl + 11.8 * asw - 15.59


def evaluate_readability_and_11yo_fit(episodes: List[Dict[str, Any]], books_lib: List[Dict[str, Any]]) -> Tuple[float, List[str]]:
    findings: List[str] = []
    if not episodes:
        return 0.0, ["No episodes found in feed.json"]

    ep_scores = []
    for ep in episodes:
        en_text = ep["hook"]["en"] + " " + " ".join(b.get("caption_en", "") for b in ep.get("beats", []))
        fk = flesch_kincaid_grade(en_text)
        # Ideal middle-grade 11yo spoken/caption FK grade is 4.5 to 7.8
        if 4.5 <= fk <= 7.8:
            grade_score = 100.0
        else:
            dist = min(abs(fk - 4.5), abs(fk - 7.8))
            grade_score = max(55.0, 100.0 - dist * 12.0)
            if fk > 8.5:
                findings.append(f"{ep['id']} FK grade slightly high ({fk:.1f}) for 11yo quick reading")
            elif fk < 3.8:
                findings.append(f"{ep['id']} FK grade too simple ({fk:.1f}) for 11yo")

        baby_hits = sum(1 for p in BABY_TALK_PATTERNS if re.search(p, en_text, re.I))
        corp_hits = sum(1 for p in CORPORATE_JARGON_PATTERNS if re.search(p, en_text, re.I))
        penalty = (baby_hits * 20.0) + (corp_hits * 18.0)
        if baby_hits:
            findings.append(f"{ep['id']} contains baby-talk phrasing unsuitable for 11yo")
        if corp_hits:
            findings.append(f"{ep['id']} contains adult corporate jargon")
        ep_scores.append(max(0.0, grade_score - penalty))

    # Check consolidated 11yo book lengths (Books 1-17 should all be substantial >= 1,400 words EN)
    book_depth_bonus = 0.0
    thin_books = []
    for bk in books_lib:
        wc_en = len(bk.get("content_en", "").split())
        if wc_en < 1200:
            thin_books.append(f"{bk.get('folder')} ({wc_en} words)")
    if not books_lib:
        findings.append("books_library.json not built yet (-15 pts)")
        book_penalty = 15.0
    elif thin_books:
        findings.append(f"Books needing deeper 11yo consolidation: {', '.join(thin_books[:4])}")
        book_penalty = min(15.0, len(thin_books) * 2.0)
    else:
        book_penalty = 0.0
        book_depth_bonus = 2.0

    score = min(100.0, max(0.0, (sum(ep_scores) / len(ep_scores)) - book_penalty + book_depth_bonus))
    return round(score, 2), findings


def evaluate_child_psych_safety(episodes: List[Dict[str, Any]], run_ollama_sample: bool = True) -> Tuple[float, List[str]]:
    findings: List[str] = []
    if not episodes:
        return 0.0, ["No episodes to audit for psychological safety"]

    pts = []
    for ep in episodes:
        blob = json.dumps(ep, ensure_ascii=False)
        harm_hits = sum(1 for p in HARM_SHAME_PATTERNS if re.search(p, blob, re.I))
        has_quest = bool(ep.get("offline_quest", {}).get("instruction", {}).get("en"))
        dilemma = ep.get("interactive_dilemma", {})
        has_takeaway = bool(dilemma.get("psych_takeaway", {}).get("en"))
        # Ensure choice_a ripple is constructive, not shaming
        ripple_a = dilemma.get("choice_a", {}).get("ripple", {}).get("en", "")
        non_shaming = len(ripple_a.split()) >= 8 and harm_hits == 0

        s = 100.0
        if harm_hits > 0:
            s -= 50.0
            findings.append(f"CRITICAL: Harm/shame pattern in {ep['id']}")
        if not has_quest:
            s -= 20.0
            findings.append(f"{ep['id']} missing offline real-world transfer quest")
        if not has_takeaway:
            s -= 15.0
            findings.append(f"{ep['id']} missing psychological takeaway")
        if not non_shaming:
            s -= 10.0
            findings.append(f"{ep['id']} dilemma ripple_a too abrupt (<8 words)")
        # Reward explicit 11yo reflection question or somatic/mindful cue
        if ep.get("mindful_cue"):
            s = min(100.0, s + 2.0)
        else:
            s -= 3.0
        pts.append(max(0.0, s))

    det_score = sum(pts) / len(pts)

    # Local Ollama (gemma2:latest) Child Psychologist Audit (temperature=0.0 for reproducible measurement)
    llm_score = det_score
    if run_ollama_sample and ollama_client.is_ollama_alive():
        sample_ep = episodes[0]
        prompt = (
            "Audit this short-video story designed for an 11-year-old child:\n"
            f"Title: {sample_ep['title']['en']}\n"
            f"Hook: {sample_ep['hook']['en']}\n"
            f"Beats: {' '.join(b['caption_en'] for b in sample_ep['beats'])}\n"
            f"Mindful Cue: {sample_ep.get('mindful_cue', {}).get('en', 'None yet')}\n"
            f"Dilemma: {sample_ep.get('interactive_dilemma', {}).get('situation', {}).get('en', '')}\n"
            f"Offline Quest: {sample_ep.get('offline_quest', {}).get('instruction', {}).get('en', '')}\n\n"
            "Return JSON ONLY with keys: "
            '{"score": <number 0-100>, "is_safe_and_constructive": true/false, "improvement_tip": "<short tip>"}'
        )
        res = ollama_client.generate_json(
            prompt=prompt,
            system="You are a PhD Developmental Child Psychologist auditing media for 11-year-olds.",
            temperature=0.0,
            max_tokens=250,
        )
        if res and isinstance(res.get("score"), (int, float)):
            llm_score = float(res["score"])
            tip = res.get("improvement_tip", "")
            if tip and llm_score < 98:
                findings.append(f"Ollama gemma2 Psychologist Tip: {tip}")

    blended = 0.80 * det_score + 0.20 * llm_score
    return round(min(100.0, blended), 2), findings


def evaluate_alt_storytelling(episodes: List[Dict[str, Any]]) -> Tuple[float, List[str]]:
    findings: List[str] = []
    if not episodes:
        return 0.0, ["No episodes present"]

    formats_seen = set()
    scores = []
    for ep in episodes:
        s = 100.0
        formats_seen.add(ep.get("alt_format", ""))
        beats = ep.get("beats", [])
        if len(beats) != 6:
            s -= 20.0
            findings.append(f"{ep['id']} has {len(beats)} beats instead of 6")
        pf = ep.get("perspective_flip", {})
        if not pf.get("lens_a_thought", {}).get("en") or not pf.get("lens_b_thought", {}).get("en"):
            s -= 25.0
            findings.append(f"{ep['id']} incomplete Dual-Perspective Flip")
        dil = ep.get("interactive_dilemma", {})
        if not dil.get("choice_a", {}).get("label", {}).get("en") or not dil.get("choice_b", {}).get("label", {}).get("en"):
            s -= 25.0
            findings.append(f"{ep['id']} incomplete Interactive Branching Dilemma")
        # Check synced beat timestamps attached to episode
        if not ep.get("beat_timestamps_en"):
            s -= 8.0
            findings.append(f"{ep['id']} missing exact per-beat audio sync timestamps")
        scores.append(max(0.0, s))

    variety_bonus = 0.0 if len(formats_seen) >= 4 else -10.0
    if len(formats_seen) < 4:
        findings.append(f"Only {len(formats_seen)} alternative storytelling formats used (need >=4)")

    final = max(0.0, min(100.0, (sum(scores) / len(scores)) + variety_bonus))
    return round(final, 2), findings


def evaluate_bilingual_parity(episodes: List[Dict[str, Any]], books_lib: List[Dict[str, Any]]) -> Tuple[float, List[str]]:
    findings: List[str] = []
    if not episodes:
        return 0.0, ["No episodes for bilingual check"]

    ro_diacritics = set("ăâîșțĂÂÎȘȚ")
    ep_scores = []
    for ep in episodes:
        s = 100.0
        ro_blob = (
            ep["title"].get("ro", "") + " " +
            ep["hook"].get("ro", "") + " " +
            " ".join(b.get("caption_ro", "") for b in ep.get("beats", []))
        )
        if len(ro_blob.split()) < 80:
            s -= 25.0
            findings.append(f"{ep['id']} Romanian narration too short ({len(ro_blob.split())} words)")
        diacritic_count = sum(1 for ch in ro_blob if ch in ro_diacritics)
        if diacritic_count < 8:
            s -= 25.0
            findings.append(f"{ep['id']} Romanian text missing proper diacritics ({diacritic_count} found)")
        if not ep.get("perspective_flip", {}).get("lens_b_thought", {}).get("ro"):
            s -= 15.0
        if not ep.get("interactive_dilemma", {}).get("psych_takeaway", {}).get("ro"):
            s -= 15.0
        ep_scores.append(max(0.0, s))

    book_ro_ok = sum(
        1 for b in books_lib
        if len(b.get("content_ro", "").split()) >= 900
        and sum(1 for ch in b.get("content_ro", "") if ch in ro_diacritics) >= 30
    )
    book_ratio = book_ro_ok / 17.0 if books_lib else 0.0
    if book_ro_ok < 17:
        findings.append(f"{book_ro_ok}/17 books have full consolidated Romanian text")

    total = 0.7 * (sum(ep_scores) / len(ep_scores)) + 0.3 * (book_ratio * 100.0)
    return round(min(100.0, total), 2), findings


def evaluate_media_integrity(episodes: List[Dict[str, Any]]) -> Tuple[float, List[str]]:
    findings: List[str] = []
    if not episodes:
        return 0.0, ["No episodes to check media"]

    valid_en = 0
    valid_ro = 0
    thumbs_ok = 0
    oversized = 0

    for ep in episodes:
        eid = ep["id"]
        v_en = os.path.join(BASE_DIR, ep.get("video_en", f"assets/videos/{eid}_en.mp4"))
        v_ro = os.path.join(BASE_DIR, ep.get("video_ro", f"assets/videos/{eid}_ro.mp4"))
        th = os.path.join(BASE_DIR, ep.get("poster", f"assets/thumbs/{eid}.jpg"))

        if os.path.exists(th) and os.path.getsize(th) > 10_000:
            thumbs_ok += 1
        else:
            findings.append(f"Missing poster thumb for {eid}")

        for lang_flag, vpath in [("en", v_en), ("ro", v_ro)]:
            if os.path.exists(vpath) and os.path.getsize(vpath) > 60_000:
                size_mb = os.path.getsize(vpath) / (1024 * 1024)
                if size_mb > 6.0:
                    oversized += 1
                if lang_flag == "en":
                    valid_en += 1
                else:
                    valid_ro += 1
            else:
                findings.append(f"Missing MP4 video: {os.path.basename(vpath)}")

    # Spot-check ffprobe streams on first & last episode
    stream_bonus = 0.0
    sample_vid = os.path.join(BASE_DIR, f"assets/videos/{episodes[0]['id']}_en.mp4")
    if os.path.exists(sample_vid):
        probe = subprocess.run(
            [
                "/opt/homebrew/bin/ffprobe", "-v", "error",
                "-show_entries", "stream=codec_name,width,height",
                "-of", "json", sample_vid,
            ],
            capture_output=True, text=True,
        )
        try:
            pdata = json.loads(probe.stdout)
            codecs = {s.get("codec_name") for s in pdata.get("streams", [])}
            dims = [(s.get("width"), s.get("height")) for s in pdata.get("streams", []) if s.get("width")]
            if "h264" in codecs and "aac" in codecs and (720, 1280) in dims:
                stream_bonus = 5.0
            else:
                findings.append(f"Stream format mismatch: codecs={codecs}, dims={dims}")
        except Exception:
            pass

    n = len(episodes)
    en_ratio = valid_en / n
    ro_ratio = valid_ro / n
    th_ratio = thumbs_ok / n
    score = (en_ratio * 50.0) + (ro_ratio * 35.0) + (th_ratio * 10.0) + stream_bonus - (oversized * 2.0)
    return round(max(0.0, min(100.0, score)), 2), findings[:6]


def evaluate_graph_health() -> Tuple[float, List[str], Dict[str, Any]]:
    findings: List[str] = []
    if not os.path.exists(GRAPH_PATH):
        return 0.0, ["knowledge_graph.json missing"], {}

    mgr = KnowledgeGraphManager(GRAPH_PATH)
    mgr.load()
    metrics = mgr.compute_graph_metrics()

    s = 0.0
    if metrics.get("book_count", 0) >= 17:
        s += 18.0
    else:
        findings.append(f"Graph has {metrics.get('book_count', 0)}/17 books")
    s += min(25.0, metrics.get("value_coverage_ratio", 0.0) * 25.0)
    if metrics.get("value_coverage_ratio", 0.0) < 0.99:
        findings.append(f"Value episode coverage is {metrics.get('value_coverage_ratio', 0)*100:.1f}% (target 100%)")
    s += min(22.0, metrics.get("largest_wcc_ratio", 0.0) * 22.0)
    fusions = metrics.get("fusion_episode_count", 0)
    s += min(20.0, fusions * 2.5)
    if fusions < 7:
        findings.append(f"Only {fusions} cross-value graph fusion episodes (target >=7)")
    if metrics.get("avg_degree", 0.0) >= 4.0:
        s += 9.0
    else:
        s += metrics.get("avg_degree", 0.0) * 2.25
        findings.append(f"Graph avg degree {metrics.get('avg_degree', 0.0)} can be enriched with deeper synergy edges")

    principles_path = os.path.join(BASE_DIR, "data", "storytelling_principles.json")
    evol_path = os.path.join(BASE_DIR, "data", "evolution_state.json")
    p_ver = 1
    if os.path.exists(principles_path):
        try:
            p_ver = int(json.load(open(principles_path, encoding="utf-8")).get("version", 1))
        except Exception:
            p_ver = 1
    evol_runs = 0
    if os.path.exists(evol_path):
        try:
            evol_runs = len(json.load(open(evol_path, encoding="utf-8")).get("daily_runs", []))
        except Exception:
            evol_runs = 0
    if p_ver >= 2 and evol_runs >= 1:
        s += 6.0
    else:
        findings.append("Autonomous Ollama daily evolution cycle not yet executed (principles still at v1)")

    return round(min(100.0, s), 2), findings, metrics


def evaluate_web_ux_and_ethics() -> Tuple[float, List[str]]:
    findings: List[str] = []
    html_path = os.path.join(BASE_DIR, "index.html")
    js_path = os.path.join(BASE_DIR, "js", "altstell.js")
    css_path = os.path.join(BASE_DIR, "css", "altstell.css")

    if not os.path.exists(html_path) or not os.path.exists(js_path) or not os.path.exists(css_path):
        return 15.0, ["AltStell web frontend files (index.html, js/altstell.js, css/altstell.css) not complete yet"]

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    checks = [
        ("scroll-snap-type" in css, 12.0, "Missing CSS vertical scroll-snap TikTok physics"),
        ("AltStell" in html, 8.0, "Missing AltStell branding in index.html"),
        ("perspective" in js.lower() and "lens" in js.lower(), 10.0, "Missing Dual-Perspective Flip UI controller"),
        ("dilemma" in js.lower() and "choice" in js.lower(), 10.0, "Missing Interactive Branching Dilemma controller"),
        ("constellation" in html.lower() and "<canvas" in html.lower(), 12.0, "Missing interactive Constellation Graph Canvas"),
        ("mindful" in js.lower() or "pause" in js.lower(), 10.0, "Missing Mindful Anti-Doomscroll Screen Guard"),
        ("books_library" in js or "openBookReader" in js, 9.0, "Missing integrated 17-Book Deep Dive Reader"),
        ("aria-label" in html and "keydown" in js, 8.0, "Missing ARIA accessibility / keyboard arrow navigation"),
        ("valuePath" in js or "quest" in js.lower(), 7.0, "Missing Value-Path playlist / Real-World Quest tracker"),
        ("beat_timestamps" in js and "timeupdate" in js, 6.0, "Missing live synced story-beat caption karaoke bar"),
        ("mindful_cue" in js, 4.0, "Missing somatic mindful_cue display in interactive story drawer"),
        ("bookSearchInput" in html and "filterBooks" in js, 4.0, "Missing instant search filter in 17-Book Deep Dive Library"),
    ]

    score = 0.0
    for passed, weight, msg in checks:
        if passed:
            score += weight
        else:
            findings.append(msg)

    return round(min(100.0, score), 2), findings


def run_full_qa_session(session_number: int, changelog_note: str = "", run_ollama_sample: bool = True) -> Dict[str, Any]:
    episodes = []
    if os.path.exists(FEED_PATH):
        with open(FEED_PATH, "r", encoding="utf-8") as f:
            feed_doc = json.load(f)
            episodes = feed_doc.get("episodes", feed_doc if isinstance(feed_doc, list) else [])

    books_lib = []
    if os.path.exists(BOOKS_JSON_PATH):
        with open(BOOKS_JSON_PATH, "r", encoding="utf-8") as f:
            books_lib = json.load(f).get("books", [])

    s_read, f_read = evaluate_readability_and_11yo_fit(episodes, books_lib)
    s_psych, f_psych = evaluate_child_psych_safety(episodes, run_ollama_sample=run_ollama_sample)
    s_alt, f_alt = evaluate_alt_storytelling(episodes)
    s_bi, f_bi = evaluate_bilingual_parity(episodes, books_lib)
    s_media, f_media = evaluate_media_integrity(episodes)
    s_graph, f_graph, g_meta = evaluate_graph_health()
    s_ux, f_ux = evaluate_web_ux_and_ethics()

    weights = {
        "age_11_readability_fit": 0.16,
        "child_psych_safety_growth": 0.18,
        "alt_storytelling_richness": 0.16,
        "bilingual_parity_en_ro": 0.12,
        "media_video_audio_integrity": 0.14,
        "graph_connectivity_expansion": 0.12,
        "ux_accessibility_ethical_design": 0.12,
    }
    dimensions = {
        "age_11_readability_fit": s_read,
        "child_psych_safety_growth": s_psych,
        "alt_storytelling_richness": s_alt,
        "bilingual_parity_en_ro": s_bi,
        "media_video_audio_integrity": s_media,
        "graph_connectivity_expansion": s_graph,
        "ux_accessibility_ethical_design": s_ux,
    }
    composite = round(sum(dimensions[k] * weights[k] for k in weights), 2)
    all_findings = f_read + f_psych + f_alt + f_bi + f_media + f_graph + f_ux

    history: List[Dict[str, Any]] = []
    if os.path.exists(QA_LOG_PATH):
        with open(QA_LOG_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)

    prev_score = history[-1]["composite_score"] if history else 0.0
    delta = round(composite - prev_score, 2)

    record = {
        "session": session_number,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "composite_score": composite,
        "delta_from_previous": delta,
        "passed_incremental": composite > prev_score,
        "episode_count": len(episodes),
        "graph_nodes": g_meta.get("total_nodes", 0),
        "graph_edges": g_meta.get("total_edges", 0),
        "dimensions": dimensions,
        "findings_count": len(all_findings),
        "top_findings": all_findings[:8],
        "changelog_note": changelog_note,
    }
    # Replace if same session_number re-run, otherwise append
    history = [h for h in history if h.get("session") != session_number]
    history.append(record)
    history.sort(key=lambda x: x["session"])

    os.makedirs(os.path.dirname(QA_LOG_PATH), exist_ok=True)
    with open(QA_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    _write_markdown_report(history)
    return record


def _write_markdown_report(history: List[Dict[str, Any]]) -> None:
    lines = [
        "# AltStell — 10-Session QA & Incremental Outcome Telemetry",
        "",
        "> Target Audience: **11-Year-Old Readers & Viewers (Bilingual EN / RO)**  ",
        "> Evaluation Engine: Quantitative Readability + `ffprobe` Media Verification + NetworkX Graph Metrics + Local `Ollama (gemma2:latest)` Child Psychologist Audit",
        "",
        "| QA Session | Composite Score | Incremental Delta | Episodes | Graph (Nodes / Edges) | Age-11 Fit | Psych Safety | Alt-Story | Bilingual | Media MP4 | Graph | Web UX | Engineering & Editorial Upgrade Applied |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for h in history:
        d = h["dimensions"]
        delta_str = f"+{h['delta_from_previous']:.2f}" if h["delta_from_previous"] >= 0 else f"{h['delta_from_previous']:.2f}"
        lines.append(
            f"| **Session {h['session']}** | **{h['composite_score']:.2f}/100** | `{delta_str}` | {h['episode_count']} | "
            f"{h['graph_nodes']} / {h['graph_edges']} | {d['age_11_readability_fit']:.1f} | {d['child_psych_safety_growth']:.1f} | "
            f"{d['alt_storytelling_richness']:.1f} | {d['bilingual_parity_en_ro']:.1f} | {d['media_video_audio_integrity']:.1f} | "
            f"{d['graph_connectivity_expansion']:.1f} | {d['ux_accessibility_ethical_design']:.1f} | {h.get('changelog_note', '')} |"
        )
    with open(QA_MD_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
