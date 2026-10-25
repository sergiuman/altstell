import os

books_metadata = {
    "8_mindset": {
        "concept": "Mindset",
        "title_en": "The Garden of Growth",
        "title_ro": "Grădina Dezvoltării",
        "5yo_en": "The Little Seed that Loved to Try",
        "5yo_ro": "Sămânța care iubea să încerce"
    },
    "9_grit": {
        "concept": "Grit",
        "title_en": "The Mountain of the Slow Climber",
        "title_ro": "Muntele Urcușului Răbdător",
        "5yo_en": "Leo's Little Wings",
        "5yo_ro": "Aripile micului Leo"
    },
    "10_deep_work": {
        "concept": "Deep Work",
        "title_en": "The Island of the Quiet Forge",
        "title_ro": "Insula Faurului Liniștit",
        "5yo_en": "The Quiet Forest",
        "5yo_ro": "Pădurea Liniștită"
    },
    "11_thinking_fast_slow": {
        "concept": "Thinking, Fast and Slow",
        "title_en": "The Hare and the Owl of the Mind",
        "title_ro": "Iepurele și Bufnița Minții",
        "5yo_en": "Quick-Hop and Slow-Hoot",
        "5yo_ro": "Iepurașul cel Rapid și Bufnița cea Înțeleaptă"
    },
    "12_quiet": {
        "concept": "Quiet",
        "title_en": "The Whispering Stream",
        "title_ro": "Pârâul Șoptitor",
        "5yo_en": "Oliver's Quiet Power",
        "5yo_ro": "Puterea liniștită a lui Oliver"
    },
    "13_boy_mole_fox_horse": {
        "concept": "The Boy, the Mole, the Fox and the Horse",
        "title_en": "The Path in the Snow",
        "title_ro": "Drumul prin zăpadă",
        "5yo_en": "Kindness in the Forest",
        "5yo_ro": "Bunătatea din pădure"
    },
    "14_start_with_why": {
        "concept": "Start With Why",
        "title_en": "The Secret of the Lighthouse",
        "title_ro": "Secretul Farului din Poiană",
        "5yo_en": "Maya's Golden Compass",
        "5yo_ro": "Busola aurie a Mayei"
    },
    "15_why_we_sleep": {
        "concept": "Why We Sleep",
        "title_en": "The Night-Garden of Dreams",
        "title_ro": "Grădina de Noapte a Viselor",
        "5yo_en": "The Sleep Elves",
        "5yo_ro": "Spiridușii Somnului"
    },
    "16_cant_hurt_me": {
        "concept": "Can't Hurt Me",
        "title_en": "The Iron Pebble",
        "title_ro": "Pietricica de Fier",
        "5yo_en": "Victor's Strong Shield",
        "5yo_ro": "Scutul puternic al lui Victor"
    },
    "17_anxious_generation": {
        "concept": "The Anxious Generation",
        "title_en": "The Glass Mirror and the Muddy Trail",
        "title_ro": "Oglinda de Sticlă și Cărarea cu Noroi",
        "5yo_en": "The Play Forest",
        "5yo_ro": "Pădurea de Joacă"
    }
}

def update_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Build new table rows
    table_rows = []
    for b, data in books_metadata.items():
        # Title replacement helper
        title_en_clean = data["title_en"].replace(" ", "_")
        title_ro_clean = data["title_ro"].replace(" ", "_")
        row = f"| **[{b}](file:///Users/sergiuman/Desktop/Books/{b}/)** | {data['concept']} | [{data['title_en']} (PDF)](file:///Users/sergiuman/Desktop/Books/{b}/{title_en_clean}_EN.pdf) <br> [Manuscris (MD)](file:///Users/sergiuman/Desktop/Books/{b}/source/{b}_en.md) | *(Nu există)* | [{data['title_ro']} (PDF)](file:///Users/sergiuman/Desktop/Books/{b}/{title_ro_clean}_RO.pdf) <br> [Manuscris (MD)](file:///Users/sergiuman/Desktop/Books/{b}/source/{b}_ro.md) |"
        table_rows.append(row)
        
    new_table_content = "\n".join(table_rows)
    
    # Insert table rows before the table end
    # We find the row 7_beyond_order and append the new rows after it
    marker_table = "7_beyond_order"
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if marker_table in line:
            new_lines.extend(table_rows)
            
    content_with_table = "\n".join(new_lines)
    
    # Build new junior edition list items
    junior_list = []
    for idx, (b, data) in enumerate(books_metadata.items(), 8):
        item = f"""* **Volumul {idx} ({data['concept']})**: *{data['5yo_en']}* / *{data['5yo_ro']}*
  * [Manuscris Engleză (MD)](file:///Users/sergiuman/Desktop/Books/junior_editions/{b}/source/manuscript_en.md) | [Fișier Audio (MP3)](file:///Users/sergiuman/Desktop/Books/junior_editions/{b}/audio_en.mp3) | [Video Premium Citire v2 (MP4)](file:///Users/sergiuman/Desktop/Books/junior_editions/{b}/video_en_v2.mp4)
  * [Manuscris Română (MD)](file:///Users/sergiuman/Desktop/Books/junior_editions/{b}/source/manuscript_ro.md) | [Fișier Audio (MP3)](file:///Users/sergiuman/Desktop/Books/junior_editions/{b}/audio_ro.mp3) | [Video Premium Citire v2 (MP4)](file:///Users/sergiuman/Desktop/Books/junior_editions/{b}/video_ro_v2.mp4)"""
        junior_list.append(item)
        
    # Insert list items after Volumul 7 beyond order
    marker_list = "Volumul 7 (Beyond Order)"
    lines = content_with_table.split("\n")
    new_lines = []
    skip = False
    for line in lines:
        if skip:
            # Skip the old placeholder lines until "Ceilalți manuscrise"
            if "Ceilalți manuscrise" in line or "---" in line:
                new_lines.extend(junior_list)
                skip = False
            else:
                continue
        new_lines.append(line)
        if marker_list in line:
            skip = True
            
    final_content = "\n".join(new_lines)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(final_content)
    print(f"[+] Successfully updated: {path}")

update_file("/Users/sergiuman/Desktop/Gemini/Books/README.md")
update_file("/Users/sergiuman/Desktop/Gemini/Books/index.md")
