"""
AltStell Vertical 9:16 Short-Video Studio (720x1280 MP4, H.264 + AAC).

Features:
- Multi-beat visual storytelling (6 timed story beats per short video)
- Zero-tremor subpixel Pillow LANCZOS camera motion (zoom + pan across high-res art)
- Dynamic glowing Constellation Graph overlay + floating firefly particles
- Crisp modern kinetic caption typography + AltStell category badge + beat progress bar
- Real spoken narration (macOS neural/system TTS: Samantha/Daniel for EN, Ioana for RO)
  mixed with warm -22dB ambient piano soundtrack and faststart web optimization (< 2.5 MB/video).
- Procedural + composite fallback art generator so autonomous daily episodes never need cloud image APIs!
"""
import hashlib
import json
import math
import os
import random
import subprocess
import tempfile
import textwrap
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
ART_DIR = os.path.join(BASE_DIR, "assets", "art")
VIDEOS_DIR = os.path.join(BASE_DIR, "assets", "videos")
THUMBS_DIR = os.path.join(BASE_DIR, "assets", "thumbs")
AMBIENT_MUSIC = os.path.join(BASE_DIR, "assets", "audio", "ambient_bed.ogg")

WIDTH = 720
HEIGHT = 1280
FPS = 24


THEME_TO_ART = {
    "emerald_forest_gears": ["systems_forest.jpg", "quiet_stream.jpg", "growth_garden.jpg"],
    "seven_keys": ["campfire_constellation.jpg", "lighthouse_why.jpg", "mountain_grit.jpg"],
    "campfire_myth": ["campfire_constellation.jpg", "systems_forest.jpg", "snow_kindness.jpg"],
    "listening_stream": ["quiet_stream.jpg", "emotional_sky.jpg", "campfire_constellation.jpg"],
    "atomic_forge": ["quiet_forge.jpg", "growth_garden.jpg", "mountain_grit.jpg"],
    "emotional_aurora": ["emotional_sky.jpg", "sleep_library.jpg", "quiet_stream.jpg"],
    "order_chaos": ["lighthouse_why.jpg", "systems_forest.jpg", "emotional_sky.jpg"],
    "growth_garden": ["growth_garden.jpg", "systems_forest.jpg", "mountain_grit.jpg"],
    "mountain_climb": ["mountain_grit.jpg", "lighthouse_why.jpg", "growth_garden.jpg"],
    "quiet_forge": ["quiet_forge.jpg", "sleep_library.jpg", "quiet_stream.jpg"],
    "mind_duality": ["mind_duality.jpg", "sleep_library.jpg", "systems_forest.jpg"],
    "quiet_power": ["quiet_stream.jpg", "quiet_forge.jpg", "snow_kindness.jpg"],
    "snowy_lantern_woods": ["snow_kindness.jpg", "campfire_constellation.jpg", "emotional_sky.jpg"],
    "lighthouse_compass": ["lighthouse_why.jpg", "campfire_constellation.jpg", "mountain_grit.jpg"],
    "sleep_library": ["sleep_library.jpg", "emotional_sky.jpg", "mind_duality.jpg"],
    "iron_resilience": ["mountain_grit.jpg", "growth_garden.jpg", "lighthouse_why.jpg"],
    "muddy_treehouse": ["muddy_trail_play.jpg", "systems_forest.jpg", "campfire_constellation.jpg"],
}

ALL_ART_FILES = [
    "systems_forest.jpg",
    "quiet_forge.jpg",
    "mind_duality.jpg",
    "mountain_grit.jpg",
    "snow_kindness.jpg",
    "sleep_library.jpg",
    "lighthouse_why.jpg",
    "muddy_trail_play.jpg",
    "growth_garden.jpg",
    "campfire_constellation.jpg",
    "quiet_stream.jpg",
    "emotional_sky.jpg",
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (99, 102, 241)


def select_art_sequence(episode: Dict[str, Any]) -> List[str]:
    """Selects 3 complementary high-res 9:16 art plates for the 6 story beats of an episode."""
    theme = episode.get("art_theme", "")
    if theme in THEME_TO_ART:
        chosen = THEME_TO_ART[theme]
    else:
        # Deterministic selection based on book_ids / category / episode id
        seed_val = int(hashlib.md5(episode["id"].encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed_val)
        available = [f for f in ALL_ART_FILES if os.path.exists(os.path.join(ART_DIR, f))]
        if len(available) >= 3:
            chosen = rng.sample(available, 3)
        else:
            chosen = available or ["systems_forest.jpg"]

    paths = [os.path.join(ART_DIR, c) for c in chosen if os.path.exists(os.path.join(ART_DIR, c))]
    if not paths:
        paths = [_create_procedural_art(episode["id"], episode.get("accent_color", "#6366f1"))]
    # Expand 3 art plates across 6 beats: [p0, p0, p1, p1, p2, p2]
    seq = []
    for i in range(6):
        seq.append(paths[(i // 2) % len(paths)])
    return seq


def _create_procedural_art(ep_id: str, accent_hex: str) -> str:
    """Generates a lush cosmic constellation landscape locally if no art file exists."""
    os.makedirs(ART_DIR, exist_ok=True)
    out_path = os.path.join(ART_DIR, f"proc_{ep_id}.jpg")
    if os.path.exists(out_path):
        return out_path
    r_acc, g_acc, b_acc = _hex_to_rgb(accent_hex)
    img = Image.new("RGB", (900, 1600), (10, 14, 34))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(1600):
        t = y / 1600.0
        r = int(12 * (1 - t) + r_acc * 0.35 * t)
        g = int(16 * (1 - t) + g_acc * 0.35 * t)
        b = int(38 * (1 - t) + b_acc * 0.45 * t)
        draw.line([(0, y), (900, y)], fill=(r, g, b, 255))
    rng = random.Random(ep_id)
    pts = [(rng.randint(80, 820), rng.randint(120, 1100)) for _ in range(18)]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dist < 260:
                draw.line([pts[i], pts[j]], fill=(r_acc, g_acc, b_acc, 95), width=2)
    for x, y in pts:
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(255, 240, 190, 220))
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.save(out_path, quality=92)
    return out_path


def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "/opt/homebrew/bin/ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return max(5.0, float(res.stdout.strip()))
    except Exception:
        return 42.0


FORMAT_LABELS_RO = {
    "RIPPLE_TIMELINE": "EFECTUL DOMINO",
    "PERSPECTIVE_FLIP": "DUBLA LENTILĂ",
    "BRANCHING_CHOICE": "ALEGEREA CĂII",
    "BRAIN_GLITCH": "CAPCANA MINȚII",
    "QUIET_SPARK": "SCÂNTEIA TĂCUTĂ",
}


def synthesize_episode_voiceover_by_beat(
    episode: Dict[str, Any], lang: str, out_mp3: str, tmpdir: str
) -> Tuple[float, List[float]]:
    """
    Synthesizes each of the 6 story beats individually via macOS TTS (`Samantha` EN / `Ioana` RO),
    measures each beat's EXACT spoken duration with ffprobe, concatenates them cleanly,
    and mixes subtle -23dB ambient piano music so visual beat switches never drift from audio!
    """
    hook_txt = episode["hook"].get(lang, episode["hook"]["en"])
    beat_key = f"caption_{lang}"
    beats_txt = [b.get(beat_key, b.get("caption_en", "")) for b in episode["beats"]]
    quest_txt = episode.get("offline_quest", {}).get("title", {}).get(lang, "")

    voice = "Ioana" if lang == "ro" else "Samantha"
    rate = "174" if lang == "ro" else "178"

    beat_wavs: List[str] = []
    beat_durs: List[float] = []

    for idx, b_txt in enumerate(beats_txt):
        if idx == 0:
            spoken = f"{hook_txt} [[slnc 320]] {b_txt} [[slnc 240]]"
        elif idx == len(beats_txt) - 1 and quest_txt:
            prefix = "Real-world spark:" if lang == "en" else "Provocarea ta reală:"
            spoken = f"{b_txt} [[slnc 300]] {prefix} {quest_txt}. [[slnc 250]]"
        else:
            spoken = f"{b_txt} [[slnc 240]]"

        aiff_p = os.path.join(tmpdir, f"beat_{idx}.aiff")
        wav_p = os.path.join(tmpdir, f"beat_{idx}.wav")
        subprocess.run(["/usr/bin/say", "-v", voice, "-r", rate, "-o", aiff_p, spoken], check=True)
        subprocess.run(
            ["/opt/homebrew/bin/ffmpeg", "-y", "-i", aiff_p, "-ac", "1", "-ar", "44100", wav_p],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        cmd_dur = [
            "/opt/homebrew/bin/ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", wav_p,
        ]
        r_dur = subprocess.run(cmd_dur, capture_output=True, text=True)
        try:
            d_sec = max(2.2, float(r_dur.stdout.strip()))
        except Exception:
            d_sec = 6.5
        beat_wavs.append(wav_p)
        beat_durs.append(d_sec)

    concat_list = os.path.join(tmpdir, "beats_concat.txt")
    with open(concat_list, "w", encoding="utf-8") as cf:
        for wp in beat_wavs:
            cf.write(f"file '{wp}'\n")

    joined_wav = os.path.join(tmpdir, "joined_voice.wav")
    subprocess.run(
        ["/opt/homebrew/bin/ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", joined_wav],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )

    if os.path.exists(AMBIENT_MUSIC):
        filter_complex = (
            "[0:a]aresample=44100,highpass=f=85,volume=1.25[v];"
            "[1:a]aresample=44100,volume=0.075,afade=t=in:st=0:d=1.2[m];"
            "[v][m]amix=inputs=2:duration=first:dropout_transition=2[out]"
        )
        subprocess.run(
            [
                "/opt/homebrew/bin/ffmpeg", "-y",
                "-i", joined_wav,
                "-stream_loop", "-1", "-i", AMBIENT_MUSIC,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-ac", "1", "-ar", "44100",
                "-codec:a", "libmp3lame", "-b:a", "96k",
                out_mp3,
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
    else:
        subprocess.run(
            [
                "/opt/homebrew/bin/ffmpeg", "-y",
                "-i", joined_wav,
                "-ac", "1", "-ar", "44100",
                "-codec:a", "libmp3lame", "-b:a", "96k",
                out_mp3,
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )

    total_d = sum(beat_durs)
    return total_d, beat_durs


def _prepare_vertical_canvas(img_path: str, accent_rgb: Tuple[int, int, int]) -> Image.Image:
    """Loads artwork and prepares a slightly oversized 840x1494 RGB plate for smooth subpixel zoom/pan."""
    img = Image.open(img_path).convert("RGB")
    target_w, target_h = 840, 1494
    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_h = target_h
        new_w = int(src_ratio * new_h)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    cropped = resized.crop((left, top, left + target_w, top + target_h))
    cropped = ImageEnhance.Color(cropped).enhance(1.08)
    return cropped


def _build_overlay_layer(
    episode: Dict[str, Any],
    beat_idx: int,
    total_beats: int,
    lang: str,
    accent_rgb: Tuple[int, int, int],
) -> Image.Image:
    """Pre-renders the crisp RGBA HUD & caption card for a single beat (100% localized for EN or RO)."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    # Top & bottom cinematic gradient vignettes for effortless readability
    for y in range(230):
        alpha = int(175 * (1.0 - y / 230.0) ** 1.5)
        draw.line([(0, y), (WIDTH, y)], fill=(8, 10, 24, alpha))
    for y in range(HEIGHT - 490, HEIGHT):
        t = (y - (HEIGHT - 490)) / 490.0
        alpha = int(225 * (t ** 1.35))
        draw.line([(0, y), (WIDTH, y)], fill=(7, 9, 22, alpha))

    font_badge = _load_font(19, bold=True)
    font_title = _load_font(26, bold=True)
    font_hook = _load_font(23, bold=True)
    font_caption = _load_font(28, bold=True)
    font_sub = _load_font(19, bold=False)

    # Top segmented story-beat bars (like Shorts / Stories)
    bar_margin = 28
    gap = 8
    seg_w = (WIDTH - 2 * bar_margin - gap * (total_beats - 1)) / total_beats
    for i in range(total_beats):
        x0 = bar_margin + i * (seg_w + gap)
        x1 = x0 + seg_w
        color = (*accent_rgb, 245) if i <= beat_idx else (255, 255, 255, 70)
        draw.rounded_rectangle([x0, 24, x1, 30], radius=3, fill=color)

    # Localized AltStell Pill Badge (zero English leakage in Romanian mode!)
    raw_fmt = episode.get("alt_format", "PERSPECTIVE_FLIP")
    if lang == "ro":
        fmt_label = FORMAT_LABELS_RO.get(raw_fmt, "POVESTE ALTERNATIVĂ")
        fusion_prefix = "FUZIUNE GRAF · " if episode.get("is_graph_fusion") else "ALTSTELL · "
    else:
        fmt_label = raw_fmt.replace("_", " ")
        fusion_prefix = "GRAPH FUSION · " if episode.get("is_graph_fusion") else "ALTSTELL · "
    badge_txt = f"{fusion_prefix}{fmt_label}"
    badge_w = min(WIDTH - 56, max(290, len(badge_txt) * 11 + 48))
    draw.rounded_rectangle([28, 46, 28 + badge_w, 82], radius=18, fill=(14, 18, 38, 205), outline=(*accent_rgb, 200), width=2)
    draw.ellipse([41, 59, 51, 69], fill=(*accent_rgb, 255))
    draw.text((60, 53), badge_txt, font=font_badge, fill=(245, 247, 255, 255))

    # Episode Title (subtle top header)
    ep_title = episode["title"].get(lang, episode["title"]["en"])
    wrapped_title = textwrap.wrap(ep_title, width=34)[:2]
    ty = 96
    for line in wrapped_title:
        draw.text((30, ty), line, font=font_title, fill=(255, 255, 255, 235))
        ty += 32

    # Bottom Glass Caption Card
    beat_obj = episode["beats"][beat_idx]
    caption_txt = beat_obj.get(f"caption_{lang}", beat_obj.get("caption_en", ""))
    if beat_idx == 0:
        hook_txt = episode["hook"].get(lang, episode["hook"]["en"])
        wrapped_hook = textwrap.wrap(f"» {hook_txt}", width=35)[:2]
    else:
        wrapped_hook = []

    wrapped_cap = textwrap.wrap(caption_txt, width=31)[:5]
    card_h = 64 + len(wrapped_cap) * 38 + (len(wrapped_hook) * 31 + 14 if wrapped_hook else 0)
    card_top = HEIGHT - 150 - card_h
    card_bot = HEIGHT - 135

    draw.rounded_rectangle(
        [24, card_top, WIDTH - 24, card_bot],
        radius=24,
        fill=(13, 17, 36, 212),
        outline=(*accent_rgb, 165),
        width=2,
    )
    # Accent left bar inside card
    draw.rounded_rectangle([38, card_top + 20, 45, card_bot - 20], radius=3, fill=(*accent_rgb, 255))

    cy = card_top + 22
    for hline in wrapped_hook:
        draw.text((60, cy), hline, font=font_hook, fill=(253, 224, 71, 255))
        cy += 31
    if wrapped_hook:
        cy += 8

    for cline in wrapped_cap:
        draw.text((60, cy), cline, font=font_caption, fill=(248, 250, 252, 255))
        cy += 38

    # Interactive prompt footer hint (100% localized, clean typography)
    hint = (
        "» Tap 'Flip Lens' or 'Choose Path' to explore"
        if lang == "en"
        else "» Apasă «Schimbă Lentila» sau «Alege Calea»"
    )
    draw.text((34, HEIGHT - 110), hint, font=font_sub, fill=(195, 206, 235, 215))

    return overlay


def render_episode_video(
    episode: Dict[str, Any],
    lang: str = "en",
    force: bool = False,
) -> Dict[str, Any]:
    """Renders a vertical 720x1280 MP4 short video + poster thumbnail for a given episode & language."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(THUMBS_DIR, exist_ok=True)

    ep_id = episode["id"]
    out_video = os.path.join(VIDEOS_DIR, f"{ep_id}_{lang}.mp4")
    out_thumb = os.path.join(THUMBS_DIR, f"{ep_id}.jpg")

    if os.path.exists(out_video) and os.path.getsize(out_video) > 50_000 and not force:
        dur = get_audio_duration(out_video)
        return {
            "ok": True,
            "video_path": out_video,
            "thumb_path": out_thumb,
            "duration_sec": round(dur, 2),
            "size_kb": round(os.path.getsize(out_video) / 1024, 1),
            "cached": True,
        }

    accent_rgb = _hex_to_rgb(episode.get("accent_color", "#6366f1"))
    art_paths = select_art_sequence(episode)

    # Save crisp clean poster thumbnail once per episode
    if not os.path.exists(out_thumb) or force:
        thumb_plate = _prepare_vertical_canvas(art_paths[0], accent_rgb)
        thumb_resized = thumb_plate.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        thumb_resized.save(out_thumb, quality=86, optimize=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        voice_mp3 = os.path.join(tmpdir, f"voice_{ep_id}_{lang}.mp3")
        total_dur, beat_durations = synthesize_episode_voiceover_by_beat(episode, lang, voice_mp3, tmpdir)

        beats = episode["beats"]
        n_beats = len(beats)
        beat_frames = [max(24, int(round(d * FPS))) for d in beat_durations]
        target_total_frames = max(n_beats * 24, int(round(total_dur * FPS)))
        beat_frames[-1] = max(24, beat_frames[-1] + (target_total_frames - sum(beat_frames)))

        # Preload prepared plates and beat overlays
        plate_cache: Dict[str, Image.Image] = {}
        for p in set(art_paths):
            plate_cache[p] = _prepare_vertical_canvas(p, accent_rgb)

        overlays = [
            _build_overlay_layer(episode, idx, n_beats, lang, accent_rgb)
            for idx in range(n_beats)
        ]

        silent_mp4 = os.path.join(tmpdir, "silent.mp4")
        ffmpeg_cmd = [
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{WIDTH}x{HEIGHT}",
            "-pix_fmt", "rgb24",
            "-r", str(FPS),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            silent_mp4,
        ]
        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        assert proc.stdin is not None

        # Deterministic firefly/constellation particles
        rng = random.Random(ep_id)
        particles = [
            (rng.uniform(0.08, 0.92), rng.uniform(0.12, 0.62), rng.uniform(2.0, 4.5), rng.uniform(0, 6.28))
            for _ in range(10)
        ]

        global_frame = 0
        for b_idx in range(n_beats):
            plate = plate_cache[art_paths[b_idx]]
            pw, ph = plate.size
            ov = overlays[b_idx]
            nf = beat_frames[b_idx]
            zoom_in = (b_idx % 2 == 0)
            pan_dir = 1.0 if (b_idx % 3 == 0) else (-1.0 if (b_idx % 3 == 1) else 0.0)

            for f_i in range(nf):
                t = f_i / max(1, nf - 1)
                # Smooth cosine easing for liquid zero-tremor subpixel motion
                ease = 0.5 - 0.5 * math.cos(math.pi * t)
                zoom = (1.02 + 0.09 * ease) if zoom_in else (1.11 - 0.09 * ease)
                crop_w = pw / zoom
                crop_h = ph / zoom
                max_dx = (pw - crop_w) * 0.5
                max_dy = (ph - crop_h) * 0.5
                cx = (pw * 0.5) + pan_dir * max_dx * (2.0 * ease - 1.0) * 0.65
                cy = (ph * 0.5) + (-pan_dir) * max_dy * (2.0 * ease - 1.0) * 0.45

                left = max(0.0, min(pw - crop_w, cx - crop_w * 0.5))
                top = max(0.0, min(ph - crop_h, cy - crop_h * 0.5))
                right = min(float(pw), left + crop_w)
                bottom = min(float(ph), top + crop_h)

                frame_bg = plate.resize(
                    (WIDTH, HEIGHT),
                    Image.Resampling.LANCZOS,
                    box=(left, top, right, bottom),
                ).convert("RGBA")

                # Subtle animated constellation fireflies in upper sky
                p_draw = ImageDraw.Draw(frame_bg, "RGBA")
                gf_sec = global_frame / FPS
                for px_n, py_n, rad, phase in particles:
                    fx = px_n * WIDTH + math.sin(gf_sec * 0.9 + phase) * 14.0
                    fy = py_n * HEIGHT + math.cos(gf_sec * 0.7 + phase) * 10.0
                    glow_a = int(95 + 85 * math.sin(gf_sec * 2.2 + phase))
                    p_draw.ellipse(
                        [fx - rad, fy - rad, fx + rad, fy + rad],
                        fill=(255, 240, 175, max(20, min(210, glow_a))),
                    )

                composed = Image.alpha_composite(frame_bg, ov).convert("RGB")
                proc.stdin.write(composed.tobytes())
                global_frame += 1

        proc.stdin.close()
        proc.wait()

        # Mux video + audio with web faststart
        subprocess.run(
            [
                "/opt/homebrew/bin/ffmpeg", "-y",
                "-i", silent_mp4,
                "-i", voice_mp3,
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "96k",
                "-shortest",
                "-movflags", "+faststart",
                out_video,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    size_kb = round(os.path.getsize(out_video) / 1024, 1)
    actual_dur = get_audio_duration(out_video)
    return {
        "ok": True,
        "video_path": out_video,
        "thumb_path": out_thumb,
        "duration_sec": round(actual_dur, 2),
        "size_kb": size_kb,
        "cached": False,
        "beat_durations": [round(bf / FPS, 2) for bf in beat_frames],
    }
