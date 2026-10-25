import os
import sys
import re
import math
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont

# Path configurations
FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
BG_COLOR = "#FDFBF7"  # Warm cream page
LINE_COLOR = "#D3C2B0"  # Soft gold/grey divider line
TEXT_COLOR = "#2A2421"  # Deep charcoal text
TITLE_COLOR = "#8C6A5C"  # Warm brown for titles
PAGE_NUMBER_COLOR = "#8C837B"

BGM_PATH = "/Users/sergiuman/Desktop/Gemini/Books/junior_editions/assets/background_music.ogg"

def get_audio_duration(audio_path):
    """Gets the duration of the audio file in seconds using ffprobe."""
    cmd = [
        "ffprobe", 
        "-v", "quiet", 
        "-print_format", "json", 
        "-show_format", 
        audio_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Error reading audio duration: {e}")
        return 400.0

def wrap_text(text, font, max_width, draw):
    """Wraps text to fit within a given pixel width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        # Use draw.textbbox to measure text width
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return lines

def parse_manuscript_to_pages(md_path, num_pages=10):
    """Parses a markdown manuscript and groups its paragraphs into exactly N pages."""
    if not os.path.exists(md_path):
        print(f"Error: Manuscript not found at {md_path}")
        return []
        
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract Title (first line with #)
    title_match = re.search(r"^#\s+(.+)$", content, re.M)
    title = title_match.group(1).strip() if title_match else "Storybook"
    
    # Extract paragraphs (lines separated by double newlines)
    paragraphs = []
    raw_paras = content.split("\n\n")
    for rp in raw_paras:
        cleaned = rp.strip()
        # Skip headers, divider marks, or empty lines
        if not cleaned or cleaned.startswith("#") or cleaned.startswith("---") or cleaned.startswith("*"):
            continue
        # Clean markdown stars
        cleaned = cleaned.replace("**", "").replace("*", "")
        paragraphs.append(cleaned)
        
    # Group paragraphs into N pages as evenly as possible
    if not paragraphs:
        return title, [""] * num_pages
        
    pages = [[] for _ in range(num_pages)]
    for idx, para in enumerate(paragraphs):
        group_idx = min(idx * num_pages // len(paragraphs), num_pages - 1)
        pages[group_idx].append(para)
        
    pages = ["\n\n".join(group) for group in pages]
        
    return title, pages

def typeset_page_image(title, text, page_num, output_img_path):
    """Draws a beautiful typeset page on a 1920x1080 canvas."""
    # 1. Create a cream canvas
    img = Image.new("RGB", (1920, 1080), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 2. Draw a vertical gold divider line
    draw.line([(1080, 0), (1080, 1080)], fill=LINE_COLOR, width=2)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype(FONT_PATH, 28)
        text_font = ImageFont.truetype(FONT_PATH, 22)
        page_font = ImageFont.truetype(FONT_PATH, 16)
    except IOError:
        # Fallback to default fonts if Georgia is not found
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        page_font = ImageFont.load_default()
        print("Warning: Georgia font not found. Using default font.")
        
    # 3. Draw Page Title (centered in the right panel)
    # Right panel starts at x=1080, ends at x=1920. Center is x=1500.
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text((1500 - (title_w / 2), 120), title, font=title_font, fill=TITLE_COLOR)
    
    # Draw a line below the title
    draw.line([(1200, 180), (1800, 180)], fill=LINE_COLOR, width=1)
    
    # 4. Draw Paragraph Text (Word-wrapped, Georgia font, right panel)
    max_text_width = 680  # 840 px total - margins
    y_cursor = 230
    line_spacing = 8
    
    paras = text.split("\n\n")
    for para in paras:
        if not para:
            continue
        wrapped_lines = wrap_text(para, text_font, max_text_width, draw)
        for line in wrapped_lines:
            line_bbox = draw.textbbox((0, 0), line, font=text_font)
            line_h = line_bbox[3] - line_bbox[1]
            
            # Left margin on right panel starts at x=1160
            draw.text((1160, y_cursor), line, font=text_font, fill=TEXT_COLOR)
            y_cursor += line_h + line_spacing
        y_cursor += 20  # Add space between paragraphs
        
    # 5. Draw Page Number
    pg_str = f"— Page {page_num} —"
    pg_bbox = draw.textbbox((0, 0), pg_str, font=page_font)
    pg_w = pg_bbox[2] - pg_bbox[0]
    draw.text((1500 - (pg_w / 2), 960), pg_str, font=page_font, fill=PAGE_NUMBER_COLOR)
    
    # Save image
    img.save(output_img_path)
    # print(f"Typeset page saved: {output_img_path}")

def compile_premium_video_v2(book_dir, language):
    """Builds the enriched read-along video (v2.0)."""
    source_dir = os.path.join(book_dir, "source")
    audio_file = os.path.join(book_dir, f"audio_{language}.mp3")
    output_file = os.path.join(book_dir, f"video_{language}_v2.mp4")
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found at {audio_file}")
        return False
        
    # 1. Get audio duration and manuscript pages
    total_duration = get_audio_duration(audio_file)
    num_pages = 10
    
    md_file = os.path.join(source_dir, f"manuscript_{language}.md")
    title, pages = parse_manuscript_to_pages(md_file, num_pages=num_pages)
    
    # Calculate page durations proportionally based on text character length
    page_lengths = [len(p) for p in pages]
    total_chars = sum(page_lengths)
    if total_chars == 0:
        page_durations = [total_duration / num_pages] * num_pages
    else:
        page_durations = [total_duration * (length / total_chars) for length in page_lengths]
        
    # Adjust final page duration to match total_duration exactly (eliminate rounding drift)
    page_durations[-1] += (total_duration - sum(page_durations))
    
    print(f"\nTotal audio duration: {total_duration:.2f} seconds")
    print("Page durations distributed proportionally:")
    for idx, d in enumerate(page_durations):
        print(f"  Page {idx+1}: {d:.2f} seconds ({page_lengths[idx]} chars)")
    
    temp_dir = os.path.join(book_dir, "temp_v2")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Typeset the 10 page backgrounds
    page_images = []
    for idx, page_content in enumerate(pages):
        img_path = os.path.join(temp_dir, f"page_{idx}.png")
        typeset_page_image(title, page_content, idx + 1, img_path)
        page_images.append(img_path)
        
    print(f"Typeset all {num_pages} pages successfully.")
    
    # 3. Generate individual video clips (panning slide + typeset page)
    clip_files = []
    
    for i in range(num_pages):
        # Determine illustration slide: Page 0,1 use slide1.png; Page 2,3 use slide2.png, etc.
        slide_idx = (i // 2) + 1
        slide_path = os.path.join(source_dir, f"slide{slide_idx}.png")
        page_bg_path = page_images[i]
        clip_path = os.path.join(temp_dir, f"clip_{i}.mp4")
        current_duration = page_durations[i]
        
        print(f"Compiling Page {i+1}/10: Using slide{slide_idx}.png with smooth Pillow zoom for {current_duration:.2f}s...")
        
        try:
            slide_img = Image.open(slide_path).convert("RGB")
            page_bg_img = Image.open(page_bg_path).convert("RGB")
            
            # Start ffmpeg process to encode raw video input
            ffmpeg_cmd = [
                "ffmpeg",
                "-f", "rawvideo",
                "-pix_fmt", "rgb24",
                "-s", "1920x1080",
                "-r", "25",
                "-i", "-",  # read from stdin
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", f"{current_duration}",
                "-y",
                clip_path
            ]
            
            process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Slide size
            slide_w, slide_h = slide_img.size
            
            # Total frames for this page
            num_frames = int(current_duration * 25)
            
            for frame_idx in range(num_frames):
                # Zoom calculation (gradual zoom in from 1.01 to 1.15)
                zoom = 1.01 + (0.14 * frame_idx / num_frames)
                
                # Max shift allowed at this zoom level to keep crop box strictly within bounds
                max_shift_x = (slide_w / 2) * (1.0 - 1.0 / zoom)
                max_shift_y = (slide_h / 2) * (1.0 - 1.0 / zoom)
                
                # Pan calculation (gradual drift from left to right, top to bottom)
                progress = -1.0 + 2.0 * (frame_idx / num_frames)
                shift_x = max_shift_x * progress
                shift_y = max_shift_y * progress
                
                cx = slide_w / 2 + shift_x
                cy = slide_h / 2 + shift_y
                
                crop_w = slide_w / zoom
                crop_h = slide_h / zoom
                
                left = max(0.0, cx - crop_w / 2)
                top = max(0.0, cy - crop_h / 2)
                right = min(float(slide_w), cx + crop_w / 2)
                bottom = min(float(slide_h), cy + crop_h / 2)
                
                # Crop and resize with LANCZOS resampling directly using the box argument!
                # This performs floating-point subpixel cropping and avoids integer rounding tremor entirely.
                cropped = slide_img.resize((1000, 1000), Image.Resampling.LANCZOS, box=(left, top, right, bottom))
                
                # Paste onto typeset page background
                frame = page_bg_img.copy()
                frame.paste(cropped, (40, 40))
                
                # Write raw RGB24 bytes to ffmpeg
                process.stdin.write(frame.tobytes())
                
            process.stdin.close()
            process.wait()
            clip_files.append(clip_path)
            
        except Exception as e:
            print(f"Error compiling page {i+1} with Pillow: {e}")
            # Fallback to a static compilation of the page background directly
            cmd_fallback = [
                "ffmpeg",
                "-loop", "1", "-i", page_bg_path,
                "-c:v", "libx264",
                "-t", f"{current_duration}",
                "-r", "25",
                "-pix_fmt", "yuv420p",
                "-y",
                clip_path
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            clip_files.append(clip_path)
            
    # 4. Write concatenation list
    concat_list_path = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")
            
    # 5. Concatenate video clips into a silent temporary video
    silent_video_path = os.path.join(temp_dir, "silent_video.mp4")
    print("Concatenating video chapters...")
    concat_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c:v", "copy",
        "-y",
        silent_video_path
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # 6. Mix audio: Voiceover + looped Background Music (Satie ogg) at -24 dB
    print("Mixing voiceover with background music and compiling final MP4...")
    
    # Check if BGM exists, if not, skip mixing and just merge voiceover
    if os.path.exists(BGM_PATH):
        # amix mixes two audio inputs.
        # [2:a]volume=0.06 loops the background music infinitely (aloop) at a quiet -24 dB
        filter_audio = (
            "[1:a]volume=1.0[voice];"
            "[2:a]volume=0.05,aloop=loop=-1:size=2e9[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first[a]"
        )
        final_cmd = [
            "ffmpeg",
            "-i", silent_video_path,
            "-i", audio_file,
            "-i", BGM_PATH,
            "-filter_complex", filter_audio,
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            output_file
        ]
    else:
        print("Warning: Background music file not found. Compiling video with voiceover only.")
        final_cmd = [
            "ffmpeg",
            "-i", silent_video_path,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            output_file
        ]
        
    try:
        subprocess.run(final_cmd, check=True)
        print(f"\n[+] SUCCESS: Premium Read-Along Video Compiled!")
        print(f"Video saved to: file://{output_file}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error during final audio/video merge: {e}")
        return False
    finally:
        # Clean up temp files
        print("Cleaning up temporary assets...")
        for clip in clip_files:
            if os.path.exists(clip):
                os.remove(clip)
        for img in page_images:
            if os.path.exists(img):
                os.remove(img)
        if os.path.exists(silent_video_path):
            os.remove(silent_video_path)
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compile_premium_video_v2.py <book_directory_path> <language_code>")
        sys.exit(1)
        
    book_dir = sys.argv[1]
    lang = sys.argv[2].lower()
    
    if not os.path.isabs(book_dir):
        book_dir = os.path.abspath(os.path.join("/Users/sergiuman/Desktop/Gemini/Books/junior_editions/", book_dir))
        
    compile_premium_video_v2(book_dir, lang)
