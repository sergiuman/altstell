import sys

def check_files(en_path, ro_path):
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()
    with open(ro_path, 'r', encoding='utf-8') as f:
        ro_text = f.read()

    en_paras = [p.strip() for p in en_text.split('\n\n') if p.strip()]
    ro_paras = [p.strip() for p in ro_text.split('\n\n') if p.strip()]

    print(f"English paragraphs: {len(en_paras)}")
    print(f"Romanian paragraphs: {len(ro_paras)}")
    
    en_word_count = len(en_text.split())
    ro_word_count = len(ro_text.split())
    print(f"English word count: {en_word_count}")
    print(f"Romanian word count: {ro_word_count}")

    if len(en_paras) != len(ro_paras):
        print("WARNING: Paragraph counts do not match!")
        min_len = min(len(en_paras), len(ro_paras))
        for i in range(min_len):
            en_words = len(en_paras[i].split())
            ro_words = len(ro_paras[i].split())
            if abs(en_words - ro_words) > 50:
                print(f"Mismatch at index {i}:")
                print(f"  EN ({en_words} w): {en_paras[i][:80]}...")
                print(f"  RO ({ro_words} w): {ro_paras[i][:80]}...")
        if len(en_paras) > len(ro_paras):
            print(f"Missing Romanian paragraphs starting from index {min_len}:")
            for i in range(min_len, len(en_paras)):
                print(f"  EN {i}: {en_paras[i][:80]}...")
        else:
            print(f"Extra Romanian paragraphs starting from index {min_len}:")
            for i in range(min_len, len(ro_paras)):
                print(f"  RO {i}: {ro_paras[i][:80]}...")
    else:
        print("SUCCESS: Paragraph counts match!")
        for i in range(len(en_paras)):
            en_words = len(en_paras[i].split())
            ro_words = len(ro_paras[i].split())
            # Just a sanity check for extremely mismatched paragraph sizes
            if en_words > 10 and ro_words < 5:
                print(f"Suspicious mismatch at paragraph {i}:")
                print(f"  EN ({en_words} w): {en_paras[i]}")
                print(f"  RO ({ro_words} w): {ro_paras[i]}")

if __name__ == '__main__':
    check_files(
        '/Users/sergiuman/Desktop/Books/6_emotional_intelligence/chapters_en/part2.md',
        '/Users/sergiuman/Desktop/Books/6_emotional_intelligence/chapters_ro/part2.md'
    )
