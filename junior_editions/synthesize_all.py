import os
import subprocess

books = [
    "8_mindset", "9_grit", "10_deep_work", "11_thinking_fast_slow",
    "12_quiet", "13_boy_mole_fox_horse", "14_start_with_why",
    "15_why_we_sleep", "16_cant_hurt_me", "17_anxious_generation"
]

api_key = os.environ.get("ELEVEN_API_KEY", "")

for b in books:
    print(f"\n==================================================")
    print(f"--- Synthesizing book {b} ---")
    print(f"==================================================")
    
    # Run the voiceover synthesis script
    env = os.environ.copy()
    env["ELEVEN_API_KEY"] = api_key
    cmd = ["python3", "/Users/sergiuman/.gemini/antigravity/brain/46163f74-df44-433c-9dbd-8cd4dcb3923b/scratch/synthesize_book_junior.py", b]
    subprocess.run(cmd, env=env, cwd="/Users/sergiuman/Desktop/Gemini/Books/junior_editions")
