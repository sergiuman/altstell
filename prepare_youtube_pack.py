import os
import shutil

metadata_mapping = {
    "1_systems_thinking": {
        "prefix": "Vol01_SystemsThinking",
        "title": "Radu & The Magic Glasses 👓 | Kids Story on Systems Thinking",
        "description": "Radu receives a pair of magical glasses that let him see how everything in the forest is connected. Help your child learn systems thinking, see the bigger picture in life, and understand cause and effect!\n\nBased on systems thinking concepts.",
        "tags": "kids story, systems thinking, educational stories, childrens book, children education, radu and magic glasses, systems thinking for kids"
    },
    "2_seven_habits": {
        "prefix": "Vol02_SevenHabits",
        "title": "Ileana's 7 Magic Keys 🔑 | 7 Habits of Happy Kids Story",
        "description": "Follow Ileana on a magical journey to find the 7 keys of happy and successful kids. A beautiful child-friendly adaptation of Sean Covey's and Stephen Covey's 7 Habits of Highly Effective People!",
        "tags": "7 habits of highly effective people, kids habits, personal growth for kids, educational stories, childrens book, happy kids"
    },
    "3_sapiens": {
        "prefix": "Vol03_Sapiens",
        "title": "The Magic Campfire 🔥 | Sapiens Story for Kids",
        "description": "Gather around the magic campfire to learn the story of us—how human beings used imagination, cooperation, and storytelling to build a beautiful world together.\n\nBased on Yuval Noah Harari's Sapiens.",
        "tags": "sapiens for kids, history for children, human history story, educational kids video, childrens bedtime story, cooperation"
    },
    "4_supercommunicators": {
        "prefix": "Vol04_Supercommunicators",
        "title": "The Whispering Hares 🐇 | How to Communicate & Connect (Kids Story)",
        "description": "Two little rabbits learn the secret of the 'whispering ears'—how to listen, understand feelings, and speak from the heart to become supercommunicators and resolve conflicts peacefully.\n\nBased on Charles Duhigg's Supercommunicators.",
        "tags": "children communication, active listening for kids, emotional intelligence, friendship story, kids communication skills, supercommunicators"
    },
    "5_atomic_habits": {
        "prefix": "Vol05_AtomicHabits",
        "title": "Tiny Steps of the Little Bear 🐻 | Atomic Habits for Kids",
        "description": "Barnaby the little bear wants to build a big wooden house. Learn how tiny, daily habits (1% better every day) can help children build big dreams and establish positive routines!\n\nBased on James Clear's Atomic Habits.",
        "tags": "atomic habits for kids, kids habits, building good habits, parenting tips, childrens growth, character development, james clear"
    },
    "6_emotional_intelligence": {
        "prefix": "Vol06_EmotionalIntelligence",
        "title": "The Heart Keepers 💖 | Emotional Intelligence Bedtime Story for Kids",
        "description": "Meet the little helpers that live inside our hearts. A beautiful storybook lesson on emotional intelligence, naming feelings, managing anger, and finding calm.\n\nBased on Daniel Goleman's Emotional Intelligence.",
        "tags": "emotional intelligence for kids, naming feelings, kids emotions, bedtime story, social emotional learning, daniel goleman"
    },
    "7_beyond_order": {
        "prefix": "Vol07_BeyondOrder",
        "title": "The Cozy Nest & The Wild Woods 🌲 | Order vs Chaos Story for Kids",
        "description": "A little bluejay learns the balance between a safe, organized nest (Order) and the exciting, unpredictable wild woods (Chaos). A lesson on rule-following, structure, and safe exploration.\n\nBased on Jordan Peterson's Beyond Order: 12 More Rules for Life.",
        "tags": "order and chaos, Jordan Peterson kids, kids life lessons, bedtime story, childrens development, rules for kids"
    },
    "8_mindset": {
        "prefix": "Vol08_Mindset",
        "title": "Pippin: The Seed that Loved to Try 🌱 | Growth Mindset Kids Story",
        "description": "Pippin the little seed learns that failing and facing rainstorms is just part of growing taller. A wonderful growth mindset story explaining that practice and effort make our brains stronger!\n\nBased on Carol S. Dweck's Mindset: The New Psychology of Success.",
        "tags": "growth mindset for kids, Carol Dweck kids, kids resilience, never give up, educational story, growth mindset story"
    },
    "9_grit": {
        "prefix": "Vol09_Grit",
        "title": "Leo's Little Wings 🏔️ | A Story of Grit & Perseverance for Kids",
        "description": "Leo the swallow is not the fastest flier, but he has something special: Grit. Learn how perseverance, pacing, and daily practice beat raw talent when climbing mountains!\n\nBased on Angela Duckworth's Grit: The Power of Passion and Perseverance.",
        "tags": "grit for kids, perseverance story, never give up, kids stamina, character building, angela duckworth, kids grit"
    },
    "10_deep_work": {
        "prefix": "Vol10_DeepWork",
        "title": "Pip's Quiet House 🐿️ | Focus & Deep Work Story for Kids",
        "description": "Pip the squirrel struggles to build his winter cabin because of the noisy forest and busy distractions. Learn how finding a quiet space and deep focus help children create amazing work.\n\nBased on Cal Newport's Deep Work.",
        "tags": "focus for kids, deep work kids, study habits, digital wellness, concentration story, cal newport children"
    },
    "11_thinking_fast_slow": {
        "prefix": "Vol11_ThinkingFastSlow",
        "title": "Quick-Hop & Slow-Hoot 🐇🦉 | Kids Story on Fast and Slow Thinking",
        "description": "Meet the rabbit and the owl inside your mind! A fun child-psychology story showing when to act fast on instinct (Quick-Hop) and when to think slowly and verify details (Slow-Hoot).\n\nBased on Daniel Kahneman's Thinking, Fast and Slow.",
        "tags": "thinking fast and slow kids, Daniel Kahneman children, critical thinking, kids psychology, decision making, logic for kids"
    },
    "12_quiet": {
        "prefix": "Vol12_Quiet",
        "title": "Oliver's Quiet Power 🦦 | Introvert Strengths Kids Story",
        "description": "Oliver the beaver is quiet and loves to draw. When the loud assembly falls into panic during a storm, Oliver's quiet observation and careful planning save the day. A celebration of introverted children!\n\nBased on Susan Cain's Quiet: The Power of Introverts.",
        "tags": "quiet power, introverted kids, introversion story, quiet strengths, childrens book, susan cain"
    },
    "13_boy_mole_fox_horse": {
        "prefix": "Vol13_BoyMoleFoxHorse",
        "title": "Kindness in the Forest ❄️ | Love, Kindness & Asking for Help (Kids Story)",
        "description": "Four friends journey through the snow and share gentle wisdom about kindness, self-compassion, and why asking for help is a sign of courage and strength.\n\nInspired by Charlie Mackesy's The Boy, the Mole, the Fox and the Horse.",
        "tags": "charlie mackesy kids, kids kindness, asking for help, self compassion, bedtime story, emotional intelligence"
    },
    "14_start_with_why": {
        "prefix": "Vol14_StartWithWhy",
        "title": "Maya's Golden Compass 🧭 | Start With Why Childrens Story",
        "description": "Maya wants to build a toy boat. She discovers that finding *why* she wants to sail (her purpose and dream) is far more important than just *what* wood she uses or *how* she constructs it.\n\nBased on Simon Sinek's Start With Why.",
        "tags": "start with why kids, Simon Sinek children, kids purpose, finding passion, dream big, young leaders"
    },
    "15_why_we_sleep": {
        "prefix": "Vol15_WhyWeSleep",
        "title": "Toby & The Sleep Elves 💤 | Why Sleep is Magic for Kids",
        "description": "Toby meets the Sleep Elves who sweep his brain-library clean and repair his muscles at night. A fun, whimsical story explaining why sleep is vital for growing bodies and minds!\n\nBased on Matthew Walker's Why We Sleep.",
        "tags": "why we sleep kids, sleep hygiene children, bedtime routine, kids sleep story, health education, matthew walker"
    },
    "16_cant_hurt_me": {
        "prefix": "Vol16_CantHurtMe",
        "title": "Victor's Strong Shield 🦔 | Building Mental Toughness Kids Story",
        "description": "Victor the hedgehog learns that his mind is stronger than any obstacle or cold rainstorm. A child-friendly adaptation of building resilience, confidence, and mental discipline.\n\nBased on David Goggins' Can't Hurt Me.",
        "tags": "mental toughness kids, David Goggins children, resilience story, building confidence, discipline for kids, kids motivation"
    },
    "17_anxious_generation": {
        "prefix": "Vol17_AnxiousGeneration",
        "title": "Dan & The Play Forest 🌳 | Digital Wellness & Outdoor Play Kids Story",
        "description": "Dan leaves his glowing magic mirror behind to climb real trees and play in the mud with his friends. A beautiful, gentle lesson on screen time, real-world connection, and childhood play.\n\nBased on Jonathan Haidt's The Anxious Generation.",
        "tags": "screen time limits kids, digital wellness children, outdoor play, childrens health, screen free childhood, jonathan haidt"
    }
}

def main():
    source_dir = "/Users/sergiuman/Desktop/Gemini/Books/junior_editions"
    dest_dir = "/Users/sergiuman/Desktop/Gemini/Books/youtube_upload_pack"
    
    os.makedirs(dest_dir, exist_ok=True)
    print(f"[+] Output folder created at: {dest_dir}")
    
    for folder, meta in metadata_mapping.items():
        # Source video path
        video_src = os.path.join(source_dir, folder, "video_en_v2.mp4")
        if not os.path.exists(video_src):
            print(f"[-] Warning: Video not found at {video_src}, skipping...")
            continue
            
        # Target paths
        video_dest = os.path.join(dest_dir, f"{meta['prefix']}_Junior_EN.mp4")
        meta_dest = os.path.join(dest_dir, f"{meta['prefix']}_Junior_EN_metadata.txt")
        
        # 1. Copy Video
        print(f"  -> Copying {folder}/video_en_v2.mp4 to {os.path.basename(video_dest)}...")
        shutil.copy2(video_src, video_dest)
        
        # 2. Write Metadata Text File
        print(f"  -> Writing metadata file: {os.path.basename(meta_dest)}...")
        with open(meta_dest, "w", encoding="utf-8") as f_meta:
            f_meta.write(f"TITLE:\n{meta['title']}\n\n")
            f_meta.write(f"DESCRIPTION:\n{meta['description']}\n\n")
            f_meta.write(f"TAGS:\n{meta['tags']}\n")
            
    print("\n[+] YouTube upload pack successfully prepared and packed!")

if __name__ == "__main__":
    main()
