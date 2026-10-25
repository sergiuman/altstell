import os
import sys
import subprocess
import json

def get_audio_duration(audio_path):
    """Gets the duration of the audio file in seconds using ffprobe."""
    print(f"Checking audio duration for: {audio_path}")
    cmd = [
        "ffprobe", 
        "-v", "quiet", 
        "-print_format", "json", 
        "-show_format", 
        "-show_streams", 
        audio_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Error reading audio duration: {e}")
        # Fallback to a default of 600 seconds (10 minutes) if ffprobe fails
        return 600.0

def compile_video(book_dir, language):
    """Compiles the slides and audio into a premium MP4 video using ffmpeg."""
    source_dir = os.path.join(book_dir, "source")
    audio_file = os.path.join(book_dir, f"audio_{language}.mp3")
    output_file = os.path.join(book_dir, f"video_{language}.mp4")
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found at {audio_file}")
        return False
        
    # Get audio duration
    total_duration = get_audio_duration(audio_file)
    print(f"Total audio duration: {total_duration:.2f} seconds")
    
    # Check for slides (slide1.png through slide5.png)
    slides = []
    for i in range(1, 6):
        slide_path = os.path.join(source_dir, f"slide{i}.png")
        if os.path.exists(slide_path):
            slides.append(slide_path)
        else:
            print(f"Warning: Slide {i} not found at {slide_path}")
            
    if not slides:
        print("Error: No slides found to compile.")
        return False
        
    num_slides = len(slides)
    slide_duration = total_duration / num_slides
    print(f"Each of the {num_slides} slides will be displayed for {slide_duration:.2f} seconds.")
    
    # Create temp directory for intermediate clips
    temp_dir = os.path.join(book_dir, "temp_clips")
    os.makedirs(temp_dir, exist_ok=True)
    
    clip_files = []
    
    # 1. Generate individual clips with a subtle Ken Burns zoompan
    for idx, slide_path in enumerate(slides):
        clip_path = os.path.join(temp_dir, f"clip_{idx}.mp4")
        print(f"Generating clip {idx+1}/{num_slides} for slide: {os.path.basename(slide_path)}")
        
        # We use a slow zoom filter: zoom starts at 1.0 and increases by 0.0003 per frame
        # We output at 1080p (1920x1080) at 25 fps.
        # d is the total number of frames. d = duration * 25 fps
        total_frames = int(slide_duration * 25)
        
        # Ffmpeg command for smooth Ken Burns zoompan
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", slide_path,
            "-vf", f"zoompan=z='min(zoom+0.0003,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1920x1080",
            "-c:v", "libx264",
            "-t", f"{slide_duration}",
            "-r", "25",
            "-pix_fmt", "yuv420p",
            "-y",
            clip_path
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            clip_files.append(clip_path)
        except subprocess.CalledProcessError:
            print("Zoompan failed, falling back to static slide clip...")
            # Fallback to a simple static image clip of the same duration
            cmd_fallback = [
                "ffmpeg",
                "-loop", "1",
                "-i", slide_path,
                "-c:v", "libx264",
                "-t", f"{slide_duration}",
                "-r", "25",
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1920:1080",
                "-y",
                clip_path
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            clip_files.append(clip_path)

    # 2. Write the list of clips to a text file for concatenation
    concat_list_path = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")
            
    # 3. Concatenate all clips and merge with the audio file
    print("Merging video clips and audio track into final MP4...")
    final_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-y",
        output_file
    ]
    
    try:
        subprocess.run(final_cmd, check=True)
        print(f"\n[+] SUCCESS: Video compiled successfully!")
        print(f"Video saved to: file://{output_file}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error during video merging: {e}")
        return False
    finally:
        # Clean up temp files
        print("Cleaning up temporary clips...")
        for clip in clip_files:
            if os.path.exists(clip):
                os.remove(clip)
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compile_youtube_video.py <book_directory_path> <language_code>")
        print("Example: python3 compile_youtube_video.py 1_systems_thinking en")
        sys.exit(1)
        
    book_dir = sys.argv[1]
    lang = sys.argv[2].lower()
    
    # Resolve relative path if needed
    if not os.path.isabs(book_dir):
        book_dir = os.path.abspath(os.path.join("/Users/sergiuman/Desktop/Gemini/Books/junior_editions/", book_dir))
        
    compile_video(book_dir, lang)
