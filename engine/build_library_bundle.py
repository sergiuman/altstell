#!/usr/bin/env python3
"""
Compiles all 17 consolidated 11-year-old books (English + Romanian Markdown + PDF links)
into `assets/books_json/books_library.json` for instant in-app Deep Dive reading on GitHub Pages.
"""
import glob
import json
import os
import re
from typing import Any, Dict, List


BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
OUT_JSON = os.path.join(BASE_DIR, "assets", "books_json", "books_library.json")


BOOK_CONFIG = [
    ("book_01", "1_systems_thinking", "Systems Thinking", "Peter Senge", "the_whispering_forest_en.md", "lumea_prin_ochii_lui_radu_ro.md", "#10b981", "The Whispering Forest", "Lumea prin ochii lui Radu"),
    ("book_02", "2_seven_habits", "The 7 Habits", "Stephen Covey", "seven_paths_of_eldoria_en.md", "ileana_si_cele_sapte_turnuri_ro.md", "#6366f1", "Seven Paths of Eldoria", "Ileana și cele șapte turnuri"),
    ("book_03", "3_sapiens", "Sapiens", "Yuval Noah Harari", "chronicles_of_the_forest_en.md", "noi_povestea_oamenilor_ro.md", "#f59e0b", "Chronicles of the Forest", "NOI: Povestea oamenilor"),
    ("book_04", "4_supercommunicators", "Supercommunicators", "Charles Duhigg", "whisperers_of_eldoria_en.md", "doar_un_pic_mai_aproape_ro.md", "#ec4899", "Whisperers of Eldoria", "Doar un pic mai aproape"),
    ("book_05", "5_atomic_habits", "Atomic Habits", "James Clear", "sparks_of_eldoria_en.md", "doar_un_pic_mai_mult_ro.md", "#f97316", "Sparks of Eldoria", "Doar un pic mai mult"),
    ("book_06", "6_emotional_intelligence", "Emotional Intelligence", "Daniel Goleman", "heart_keepers_of_eldoria_en.md", "doar_un_pic_mai_adanc_ro.md", "#a855f7", "Heart Keepers of Eldoria", "Doar un pic mai adânc"),
    ("book_07", "7_beyond_order", "Beyond Order", "Jordan B. Peterson", "beyond_the_whispering_valley_en.md", "doar_un_pic_mai_putin_haos_ro.md", "#14b8a6", "Beyond the Whispering Valley", "Doar un pic mai puțin haos"),
    ("book_08", "8_mindset", "Mindset", "Carol S. Dweck", "8_mindset_en.md", "8_mindset_ro.md", "#22c55e", "The Garden of Growth", "Grădina Dezvoltării"),
    ("book_09", "9_grit", "Grit", "Angela Duckworth", "9_grit_en.md", "9_grit_ro.md", "#eab308", "The Mountain of the Slow Climber", "Muntele Urcușului Răbdător"),
    ("book_10", "10_deep_work", "Deep Work", "Cal Newport", "10_deep_work_en.md", "10_deep_work_ro.md", "#3b82f6", "The Island of the Quiet Forge", "Insula Faurului Liniștit"),
    ("book_11", "11_thinking_fast_slow", "Thinking, Fast and Slow", "Daniel Kahneman", "11_thinking_fast_slow_en.md", "11_thinking_fast_slow_ro.md", "#06b6d4", "The Hare and the Owl of the Mind", "Iepurele și Bufnița Minții"),
    ("book_12", "12_quiet", "Quiet", "Susan Cain", "12_quiet_en.md", "12_quiet_ro.md", "#8b5cf6", "The Whispering Stream", "Pârâul Șoptitor"),
    ("book_13", "13_boy_mole_fox_horse", "The Boy, the Mole, the Fox and the Horse", "Charlie Mackesy", "13_boy_mole_fox_horse_en.md", "13_boy_mole_fox_horse_ro.md", "#f43f5e", "The Path in the Snow", "Drumul prin zăpadă"),
    ("book_14", "14_start_with_why", "Start With Why", "Simon Sinek", "14_start_with_why_en.md", "14_start_with_why_ro.md", "#fbbf24", "The Secret of the Lighthouse", "Secretul Farului din Poiană"),
    ("book_15", "15_why_we_sleep", "Why We Sleep", "Matthew Walker", "15_why_we_sleep_en.md", "15_why_we_sleep_ro.md", "#818cf8", "The Night-Garden of Dreams", "Grădina de Noapte a Viselor"),
    ("book_16", "16_cant_hurt_me", "Can't Hurt Me (Resilience Adaptation)", "David Goggins", "16_cant_hurt_me_en.md", "16_cant_hurt_me_ro.md", "#ef4444", "The Iron Pebble", "Pietricica de Fier"),
    ("book_17", "17_anxious_generation", "The Anxious Generation", "Jonathan Haidt", "17_anxious_generation_en.md", "17_anxious_generation_ro.md", "#10b981", "The Glass Mirror and the Muddy Trail", "Oglinda de Sticlă și Cărarea cu Noroi"),
]


def _extract_chapters(md_text: str, max_chars: int = 26000) -> List[Dict[str, str]]:
    """Splits markdown into readable chapter sections for the in-app 11yo reader."""
    trimmed = md_text[:max_chars]
    parts = re.split(r"(?m)^(#{1,2}\s+.+)$", trimmed)
    chapters: List[Dict[str, str]] = []
    curr_title = "Introduction"
    curr_body: List[str] = []

    for chunk in parts:
        c = chunk.strip()
        if not c:
            continue
        if re.match(r"^#{1,2}\s+", c):
            if curr_body:
                chapters.append({"heading": curr_title, "body": "\n\n".join(curr_body)})
                curr_body = []
            curr_title = re.sub(r"^#{1,2}\s+", "", c).strip()
        else:
            curr_body.append(c)

    if curr_body:
        chapters.append({"heading": curr_title, "body": "\n\n".join(curr_body)})

    return chapters[:10] if chapters else [{"heading": "Story", "body": trimmed}]


def _find_pdfs(folder_path: str) -> Dict[str, str]:
    pdfs = sorted(glob.glob(os.path.join(folder_path, "*.pdf")))
    pdf_en = ""
    pdf_ro = ""
    for p in pdfs:
        rel = os.path.relpath(p, BASE_DIR)
        if "_EN.pdf" in p or "EN.pdf" in p:
            pdf_en = rel
        elif "_RO.pdf" in p or "RO.pdf" in p:
            if not pdf_ro:
                pdf_ro = rel
    return {"pdf_en": pdf_en, "pdf_ro": pdf_ro}


def build_library() -> Dict[str, Any]:
    books_out = []
    for idx, (bid, folder, source_book, author, md_en_name, md_ro_name, color, title_en, title_ro) in enumerate(BOOK_CONFIG, 1):
        fdir = os.path.join(BASE_DIR, folder)
        en_path = os.path.join(fdir, "source", md_en_name)
        ro_path = os.path.join(fdir, "source", md_ro_name)

        en_text = open(en_path, "r", encoding="utf-8").read() if os.path.exists(en_path) else ""
        ro_text = open(ro_path, "r", encoding="utf-8").read() if os.path.exists(ro_path) else ""

        pdfs = _find_pdfs(fdir)

        books_out.append({
            "id": bid,
            "num": idx,
            "folder": folder,
            "source_book": source_book,
            "source_author": author,
            "color": color,
            "title_en": title_en,
            "title_ro": title_ro,
            "word_count_en": len(en_text.split()),
            "word_count_ro": len(ro_text.split()),
            "pdf_en": pdfs["pdf_en"],
            "pdf_ro": pdfs["pdf_ro"],
            "content_en": en_text[:28000],
            "content_ro": ro_text[:28000],
            "chapters_en": _extract_chapters(en_text),
            "chapters_ro": _extract_chapters(ro_text),
        })

    doc = {
        "total_books": len(books_out),
        "target_age": 11,
        "books": books_out,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"[+] Built books_library.json with {len(books_out)} bilingual 11yo books!")
    return doc


if __name__ == "__main__":
    build_library()
