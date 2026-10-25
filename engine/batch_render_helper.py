#!/usr/bin/env python3
"""Parallel batch MP4 short-video renderer + feed timestamp updater for AltStell."""
import argparse
import concurrent.futures
import json
import os
import sys
import time
from typing import Any, Dict, Tuple

BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.graph_engine import FEED_PATH
from engine.render_short_videos import render_episode_video


def _worker(args: Tuple[Dict[str, Any], str, bool]) -> Tuple[str, Dict[str, Any]]:
    ep, lang, force = args
    res = render_episode_video(ep, lang=lang, force=force)
    return ep["id"], res


def run_batch(start_idx: int, end_idx: int, lang: str, workers: int = 4, force: bool = True) -> None:
    t0 = time.time()
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        feed_doc = json.load(f)
    episodes = feed_doc["episodes"]
    subset = episodes[start_idx:end_idx]

    tasks = [(ep, lang, force) for ep in subset]
    results: Dict[str, Dict[str, Any]] = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        for eid, res in ex.map(_worker, tasks):
            results[eid] = res
            print(f"[+] {eid}_{lang}.mp4 -> {res['duration_sec']}s ({res['size_kb']} KB)", flush=True)

    for ep in subset:
        eid = ep["id"]
        r = results[eid]
        ep["video_en"] = f"assets/videos/{eid}_en.mp4"
        ep["video_ro"] = f"assets/videos/{eid}_ro.mp4"
        ep["poster"] = f"assets/thumbs/{eid}.jpg"
        ep[f"duration_{lang}_sec"] = r["duration_sec"]
        bdurs = r.get("beat_durations", [7.0] * 6)
        starts = []
        acc = 0.0
        for d in bdurs:
            starts.append(round(acc, 2))
            acc += d
        ep[f"beat_timestamps_{lang}"] = starts

    with open(FEED_PATH, "w", encoding="utf-8") as f:
        json.dump(feed_doc, f, ensure_ascii=False, indent=2)

    print(f"[✓] Batch [{start_idx}:{end_idx}] ({lang}) completed in {time.time() - t0:.1f}s!")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=12)
    p.add_argument("--lang", type=str, default="en")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--no-force", action="store_true")
    a = p.parse_args()
    run_batch(a.start, a.end, a.lang, workers=a.workers, force=not a.no_force)
