import os
import re
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# ----------------------------------------------------
# FONT REGISTRATION (TrueType for diacritic support)
# ----------------------------------------------------
FONT_REGULAR = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONT_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT_ITALIC = '/System/Library/Fonts/Supplemental/Arial Italic.ttf'

try:
    pdfmetrics.registerFont(TTFont('Arial', FONT_REGULAR))
    pdfmetrics.registerFont(TTFont('Arial-Bold', FONT_BOLD))
    pdfmetrics.registerFont(TTFont('Arial-Italic', FONT_ITALIC))
    FONT_FAMILY = 'Arial'
except Exception as e:
    print(f"Warning: Could not register Arial fonts ({e}). Falling back to Helvetica.")
    FONT_FAMILY = 'Helvetica'

# ----------------------------------------------------
# TWO-PASS CANVAS FOR PAGE NUMBERING ("Page X of Y")
# ----------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont(FONT_FAMILY if FONT_FAMILY != 'Arial' else 'Arial', 9)
        self.setFillColor(HexColor('#3b2d4a'))
        
        # Get dimensions
        width, height = self._pagesize
        
        # Draw running header
        book_title = self.get_book_title()
        self.drawString(64, height - 54, book_title)
        
        # Draw header separator line
        self.setStrokeColor(HexColor('#b5a9c2'))
        self.setLineWidth(0.5)
        self.line(64, height - 60, width - 64, height - 60)
        
        # Draw running footer line
        self.line(64, 50, width - 64, 50)
        
        page_str = f"Page {self._pageNumber} of {page_count}" if self.is_english() else f"Pagina {self._pageNumber} din {page_count}"
        self.drawRightString(width - 64, 35, page_str)
        self.drawString(64, 35, "Adapted for Children" if self.is_english() else "Adaptat pentru copii")
        
        self.restoreState()

    def get_book_title(self):
        # Infer title from filename
        fn = os.path.basename(self._filename).replace(".pdf", "").replace("_", " ")
        return fn

    def is_english(self):
        return "ro" not in os.path.basename(self._filename).lower()

# ----------------------------------------------------
# MARKDOWN TO HTML INLINE PARSER
# ----------------------------------------------------
def parse_inline_styles(text):
    text = text.replace('_', '*')
    tokens = re.split(r'(\*\*\*|\*\*|\*)', text)
    result = []
    stack = []
    
    for token in tokens:
        if token == '***':
            if 'italic' in stack and 'bold' in stack:
                while stack:
                    open_tag = stack.pop()
                    if open_tag == 'bold':
                        result.append('</b>')
                    elif open_tag == 'italic':
                        result.append('</i>')
            elif 'bold' in stack:
                stack.remove('bold')
                result.append('</b><i>')
                stack.append('italic')
            elif 'italic' in stack:
                stack.remove('italic')
                result.append('</i><b>')
                stack.append('bold')
            else:
                result.append('<b><i>')
                stack.append('bold')
                stack.append('italic')
        elif token == '**':
            if 'bold' in stack:
                while stack:
                    tag = stack.pop()
                    if tag == 'bold':
                        result.append('</b>')
                        break
                    elif tag == 'italic':
                        result.append('</i>')
            else:
                result.append('<b>')
                stack.append('bold')
        elif token == '*':
            if 'italic' in stack:
                while stack:
                    tag = stack.pop()
                    if tag == 'italic':
                        result.append('</i>')
                        break
                    elif tag == 'bold':
                        result.append('</b>')
            else:
                result.append('<i>')
                stack.append('italic')
        else:
            result.append(token)
            
    while stack:
        tag = stack.pop()
        if tag == 'bold':
            result.append('</b>')
        elif tag == 'italic':
            result.append('</i>')
            
    return "".join(result)

def parse_markdown_to_story(md_path, styles, title, subtitle, author):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} does not exist.")
        return []
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pre-process inline bold and italics
    content = parse_inline_styles(content)
    
    story = []
    
    # 1. Add Cover Page Elements
    story.append(Spacer(1, 100))
    story.append(Paragraph(title, styles['CoverTitle']))
    story.append(Spacer(1, 15))
    story.append(Paragraph(subtitle, styles['CoverSubtitle']))
    story.append(Spacer(1, 150))
    story.append(Paragraph(author, styles['CoverAuthor']))
    story.append(PageBreak())
    
    # 2. Add Content
    blocks = content.split('\n\n')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Parse titles (# Title)
        if block.startswith('# ') or block.startswith('## '):
            level = 1 if block.startswith('# ') else 2
            text = block[2 if level == 1 else 3:].strip()
            # If it's a major heading, put it on a new page
            story.append(PageBreak())
            story.append(Spacer(1, 40))
            story.append(Paragraph(text, styles['PartHeading'] if level == 1 else styles['ChapterHeading']))
            story.append(Spacer(1, 20))
            
        # Parse subheadings (### Title)
        elif block.startswith('### '):
            text = block[4:].strip()
            story.append(Spacer(1, 12))
            story.append(Paragraph(text, styles['SubHeading']))
            story.append(Spacer(1, 8))
            
        # Parse bulleted lists
        elif block.startswith('* ') or block.startswith('- ') or re.match(r'^\d+\.\s', block):
            lines = block.split('\n')
            for line in lines:
                line_cleaned = re.sub(r'^[\*\-\d\.]+\s+', '', line).strip()
                story.append(Paragraph(f"• {line_cleaned}", styles['BodyText']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 8))
            
        # Parse blockquotes (> text)
        elif block.startswith('> '):
            text = block[2:].strip()
            story.append(Spacer(1, 6))
            story.append(Paragraph(text, styles['BlockQuote']))
            story.append(Spacer(1, 8))
            
        # Parse horizontal lines
        elif block == '---':
            continue
            
        # Normal paragraphs
        else:
            story.append(Paragraph(block.replace('\n', ' '), styles['BodyText']))
            story.append(Spacer(1, 14))
            
    return story

def compile_pdf(md_path, pdf_path, title, subtitle, author):
    # Setup styles
    styles = getSampleStyleSheet()
    color_title = HexColor('#281230')
    color_text = HexColor('#212529')
    
    # Remove standard styles to avoid name collisions
    for name in ['CoverTitle', 'CoverSubtitle', 'CoverAuthor', 'PartHeading', 'ChapterHeading', 'SubHeading', 'BlockQuote']:
        if name in styles:
            styles.byName.pop(name)
            
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=color_title,
        alignment=1,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Arial-Italic' if FONT_FAMILY == 'Arial' else 'Helvetica-Oblique',
        fontSize=16,
        leading=20,
        textColor=HexColor('#543368'),
        alignment=1,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='CoverAuthor',
        fontName='Arial' if FONT_FAMILY == 'Arial' else 'Helvetica',
        fontSize=12,
        leading=16,
        textColor=HexColor('#654881'),
        alignment=1,
    ))
    
    styles.add(ParagraphStyle(
        name='PartHeading',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=color_title,
        alignment=1,
        spaceAfter=25
    ))
    
    styles.add(ParagraphStyle(
        name='ChapterHeading',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=color_title,
        keepWithNext=True,
        spaceBefore=15,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='SubHeading',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=color_title,
        spaceBefore=10,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='BlockQuote',
        fontName='Arial-Italic' if FONT_FAMILY == 'Arial' else 'Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=HexColor('#495057'),
        leftIndent=20,
        rightIndent=20,
        spaceBefore=8,
        spaceAfter=8
    ))
    
    # Update BodyText
    body_style = styles['BodyText']
    body_style.fontName = 'Arial' if FONT_FAMILY == 'Arial' else 'Helvetica'
    body_style.fontSize = 11
    body_style.leading = 16
    body_style.textColor = color_text
    
    # Create Document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    story = parse_markdown_to_story(md_path, styles, title, subtitle, author)
    
    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Success: Compiled {pdf_path}")

def main():
    books_data = {
        "8_mindset": {
            "title_en": "The Garden of Growth",
            "title_ro": "Grădina Dezvoltării",
            "sub_en": "Based on the psychology of success by Carol S. Dweck",
            "sub_ro": "Bazat pe psihologia succesului de Carol S. Dweck",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "9_grit": {
            "title_en": "The Mountain of the Slow Climber",
            "title_ro": "Muntele Urcușului Răbdător",
            "sub_en": "Based on the power of passion and perseverance by Angela Duckworth",
            "sub_ro": "Bazat pe puterea pasiunii și perseverenței de Angela Duckworth",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "10_deep_work": {
            "title_en": "The Island of the Quiet Forge",
            "title_ro": "Insula Faurului Liniștit",
            "sub_en": "Based on focus in a distracted world by Cal Newport",
            "sub_ro": "Bazat pe concentrare într-o lume agitată de Cal Newport",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "11_thinking_fast_slow": {
            "title_en": "The Hare and the Owl of the Mind",
            "title_ro": "Iepurele și Bufnița Minții",
            "sub_en": "Based on Daniel Kahneman's thinking systems",
            "sub_ro": "Bazat pe sistemele de gândire ale lui Daniel Kahneman",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "12_quiet": {
            "title_en": "The Whispering Stream",
            "title_ro": "Pârâul Șoptitor",
            "sub_en": "Based on the power of introverts by Susan Cain",
            "sub_ro": "Bazat pe puterea introvertiților de Susan Cain",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "13_boy_mole_fox_horse": {
            "title_en": "The Path in the Snow",
            "title_ro": "Drumul prin zăpadă",
            "sub_en": "Based on the wisdom of Charlie Mackesy",
            "sub_ro": "Bazat pe înțelepciunea lui Charlie Mackesy",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "14_start_with_why": {
            "title_en": "The Secret of the Lighthouse",
            "title_ro": "Secretul Farului din Poiană",
            "sub_en": "Based on finding your purpose by Simon Sinek",
            "sub_ro": "Bazat pe descoperirea scopului de Simon Sinek",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "15_why_we_sleep": {
            "title_en": "The Night-Garden of Dreams",
            "title_ro": "Grădina de Noapte a Viselor",
            "sub_en": "Based on the science of sleep by Matthew Walker",
            "sub_ro": "Bazat pe știința somnului de Matthew Walker",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "16_cant_hurt_me": {
            "title_en": "The Iron Pebble",
            "title_ro": "Pietricica de Fier",
            "sub_en": "Based on resilience and mental discipline by David Goggins",
            "sub_ro": "Bazat pe reziliență și disciplină mentală de David Goggins",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        },
        "17_anxious_generation": {
            "title_en": "The Glass Mirror and the Muddy Trail",
            "title_ro": "Oglinda de Sticlă și Cărarea cu Noroi",
            "sub_en": "Based on screen wellness and real-world play by Jonathan Haidt",
            "sub_ro": "Bazat pe echilibrul digital și jocul în lumea reală de Jonathan Haidt",
            "author_en": "Adapted for Children",
            "author_ro": "Adaptat pentru copii"
        }
    }
    
    for folder, data in books_data.items():
        base_dir = f"/Users/sergiuman/Desktop/Gemini/Books/{folder}"
        
        # English PDF
        md_en = os.path.join(base_dir, f"source/{folder}_en.md")
        pdf_en = os.path.join(base_dir, f"{data['title_en'].replace(' ', '_')}_EN.pdf")
        compile_pdf(md_en, pdf_en, data['title_en'], data['sub_en'], data['author_en'])
        
        # Romanian PDF
        md_ro = os.path.join(base_dir, f"source/{folder}_ro.md")
        pdf_ro = os.path.join(base_dir, f"{data['title_ro'].replace(' ', '_')}_RO.pdf")
        compile_pdf(md_ro, pdf_ro, data['title_ro'], data['sub_ro'], data['author_ro'])

if __name__ == "__main__":
    main()
