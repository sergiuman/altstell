import os
import re
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
        
        # Footer text
        footer_text = self.get_footer_text()
        self.drawString(64, 35, footer_text)
        
        self.restoreState()

    def get_book_title(self):
        filename = self._filename.lower()
        if "pastratorii" in filename:
            return "Păstrătorii Inimii din Eldoria — Furtunile Inimii"
        elif "adanc" in filename or "adânc" in filename:
            return "Doar un pic mai adânc — Inteligență Emoțională"
        return "Heart Keepers of Eldoria — The Tempests of the Heart"

    def get_footer_text(self):
        filename = self._filename.lower()
        if "pastratorii" in filename:
            return "Păstrătorii Inimii din Eldoria"
        elif "adanc" in filename or "adânc" in filename:
            return "Doar un pic mai adânc"
        return "Heart Keepers of Eldoria"

    def is_english(self):
        filename = self._filename.lower()
        return "heart" in filename or "en.pdf" in filename

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
                temp_stack = []
                while stack:
                    tag = stack.pop()
                    if tag == 'bold':
                        result.append('</b>')
                        break
                    else:
                        if tag == 'italic':
                            result.append('</i>')
                        temp_stack.append(tag)
                while temp_stack:
                    tag = temp_stack.pop()
                    if tag == 'italic':
                        result.append('<i>')
                    stack.append(tag)
            else:
                result.append('<b>')
                stack.append('bold')
        elif token == '*':
            if 'italic' in stack:
                temp_stack = []
                while stack:
                    tag = stack.pop()
                    if tag == 'italic':
                        result.append('</i>')
                        break
                    else:
                        if tag == 'bold':
                            result.append('</b>')
                        temp_stack.append(tag)
                while temp_stack:
                    tag = temp_stack.pop()
                    if tag == 'bold':
                        result.append('<b>')
                    stack.append(tag)
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

# ----------------------------------------------------
# MARKDOWN TO PLATYPUS PARSER
# ----------------------------------------------------
def parse_markdown_to_story(md_path, styles):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} does not exist.")
        return []
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('\r\n***\r\n', '\n---\n').replace('\n***\n', '\n---\n')

    story = []
    
    # Pre-process bold and italics to fit ReportLab HTML tag structure cleanly
    content = parse_inline_styles(content)
    
    # Split content into paragraphs/headings by double newlines or lines
    blocks = content.split('\n\n')
    
    is_cover = True
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Parse Cover Title (only if is_cover is True)
        if block.startswith('# ') and is_cover:
            title_text = block[2:].strip().replace('\n', '<br/>')
            story.append(Spacer(1, 120))
            story.append(Paragraph(title_text, styles['CoverTitle']))
            story.append(Spacer(1, 20))
            
        # Parse Subtitle (only if is_cover is True)
        elif block.startswith('*') and block.endswith('*') and is_cover:
            subtitle_text = block[1:-1].strip().replace('\n', '<br/>')
            story.append(Paragraph(subtitle_text, styles['CoverSubtitle']))
            
        # Parse Written by / metadata block
        elif is_cover and ("<!-- de -->" in block or "Written by" in block or "Scris de" in block or "de Sergiu" in block or "de MULT CURAJ" in block or "de" in block):
            story.append(Spacer(1, 180))
            story.append(Paragraph(block.replace('\n', '<br/>'), styles['CoverAuthor']))
            story.append(PageBreak())
            is_cover = False # Cover page completed
            
        # Parse Part Headings and front-matter titles (# Heading when not on cover)
        elif block.startswith('# ') and not is_cover:
            heading_text = block[2:].strip()
            story.append(PageBreak())
            story.append(Spacer(1, 100))
            story.append(Paragraph(heading_text, styles['PartHeading']))
            story.append(Spacer(1, 30))
            
        # Parse Chapter Headings / Glossary (## Heading when not on cover)
        elif block.startswith('## ') and not is_cover:
            chapter_title = block[3:].strip().replace('\n', '<br/>')
            story.append(PageBreak()) # EVERY chapter on a new page!
            story.append(Spacer(1, 30))
            story.append(Paragraph(chapter_title, styles['ChapterHeading']))
            story.append(Spacer(1, 15))
            
        # Parse Subheadings / glossary terms (### Heading when not on cover)
        elif block.startswith('### ') and not is_cover:
            sub_title = block[4:].strip()
            story.append(Spacer(1, 10))
            story.append(Paragraph(sub_title, styles['SubHeading']))
            story.append(Spacer(1, 6))
            
        # Parse horizontal line (---)
        elif block == '---':
            continue
            
        # Parse numbered lists
        elif re.match(r'^\d+\.\s', block):
            list_items = block.split('\n')
            for item in list_items:
                item_cleaned = re.sub(r'^\d+\.\s', '', item).strip()
                story.append(Paragraph(f"• {item_cleaned}", styles['BodyText']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 10))
            
        # Parse blockquotes (e.g. > *Quote*)
        elif block.startswith('> '):
            quote_text = block[2:].strip()
            story.append(Spacer(1, 6))
            story.append(Paragraph(quote_text, styles['BlockQuote']))
            story.append(Spacer(1, 10))
            
        # Parse normal paragraphs
        else:
            story.append(Paragraph(block.replace('\n', ' '), styles['BodyText']))
            story.append(Spacer(1, 14))
            
    return story

def check_romanian_headings(md_path):
    if not os.path.exists(md_path):
        return
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('\r\n***\r\n', '\n---\n').replace('\n***\n', '\n---\n')
    
    # English stopwords to flag in Romanian headings
    stopwords = [r'\bPart\b', r'\bChapter\b', r'\bThe\b', r'\bof\b']
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        line_strip = line.strip()
        if line_strip.startswith('# ') or line_strip.startswith('## '):
            for stop in stopwords:
                if re.search(stop, line_strip, re.IGNORECASE):
                    raise ValueError(f"CRITICAL ERROR: English heading pattern found in Romanian manuscript '{md_path}' at line {i}: '{line_strip}'")

# ----------------------------------------------------
# STANDARD TYPESETTING COMPILATION (Letter size, normal fonts)
# ----------------------------------------------------
def build_normal_pdf(parts_dir, output_pdf, language='en'):
    print(f"\n--- Compiling {output_pdf} (Normal Standard Typesetting) ---")
    
    # 1. Combine all part files sequentially to create temporary file for ReportLab
    temp_md_path = f"temp_book_{language}.md"
    parts = ["part1.md", "part2.md", "part3.md", "part4.md", "part5.md"]
    
    with open(temp_md_path, 'w', encoding='utf-8') as outfile:
        # Add book title and cover header
        if language == 'en':
            outfile.write("# The Heart-Keepers of Eldoria\n*Emotional Intelligence for Kids*\n\n<!-- de -->\n\n---\n\n")
        elif language == 'ro_eldoria':
            outfile.write("# PĂSTRĂTORII INIMII DIN ELDORIA\n*Furtunile Inimii*\n\n<!-- de -->\n\n---\n\n")
        else: # ro_custom
            outfile.write("# DOAR UN PIC MAI ADÂNC\n*Povestea lui Alex, a unei pisici pe nume Filozoful și a furtunilor care trec dacă le dai un nume*\n\n" "<!-- de -->" "\n\n---\n\n")
            
        for part in parts:
            part_path = os.path.join(parts_dir, part)
            if os.path.exists(part_path):
                with open(part_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")
    
    styles = getSampleStyleSheet()
    
    # Standard document formatting styles
    color_title = HexColor('#281230')
    color_text = HexColor('#212529')
    
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=color_title,
        alignment=1,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Arial-Italic' if FONT_FAMILY == 'Arial' else 'Helvetica-Oblique',
        fontSize=14,
        leading=18,
        textColor=HexColor('#543368'),
        alignment=1,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='CoverAuthor',
        fontName='Arial' if FONT_FAMILY == 'Arial' else 'Helvetica',
        fontSize=10,
        leading=14,
        textColor=HexColor('#654881'),
        alignment=1,
    ))
    
    styles.add(ParagraphStyle(
        name='PartHeading',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=color_title,
        alignment=1,
        spaceAfter=25
    ))
    
    styles.add(ParagraphStyle(
        name='ChapterHeading',
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=color_title,
        keepWithNext=True,
        spaceBefore=15,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Normal'],
        fontName='Arial-Bold' if FONT_FAMILY == 'Arial' else 'Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=color_title,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='BlockQuote',
        parent=styles['Normal'],
        fontName='Arial-Italic' if FONT_FAMILY == 'Arial' else 'Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=HexColor('#4e3d59'),
        leftIndent=24,
        rightIndent=24,
        spaceBefore=8,
        spaceAfter=8
    ))
    
    styles['BodyText'].fontName = 'Arial' if FONT_FAMILY == 'Arial' else 'Helvetica'
    styles['BodyText'].fontSize = 11.5
    styles['BodyText'].leading = 16.5
    styles['BodyText'].textColor = color_text
    styles['BodyText'].spaceAfter = 12
    
    # Premium Letter Size template (8.5 x 11 inches) with 0.94 margin (68pt)
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=68,
        rightMargin=68,
        topMargin=68,
        bottomMargin=68
    )
    
    story = parse_markdown_to_story(temp_md_path, styles)
    
    # Compile PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Clean up temp file
    if os.path.exists(temp_md_path):
        os.remove(temp_md_path)
        
    print(f"Finished {output_pdf}. Compiled page count: {doc.page}")

def concatenate_manuscript(parts_dir, output_md):
    parts = ["part1.md", "part2.md", "part3.md", "part4.md", "part5.md"]
    with open(output_md, 'w', encoding='utf-8') as outfile:
        for i, part in enumerate(parts):
            part_path = os.path.join(parts_dir, part)
            if os.path.exists(part_path):
                with open(part_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    if i < len(parts) - 1:
                        outfile.write("\n\n")
    print(f"Concatenated manuscript saved to {output_md}")

if __name__ == '__main__':
    # English
    if os.path.exists('chapters_en') and os.listdir('chapters_en'):
        concatenate_manuscript('chapters_en', 'heart_keepers_of_eldoria_en.md')
        build_normal_pdf('chapters_en', '../Heart_Keepers_of_Eldoria_EN.pdf', 'en')
    
    # Romanian Custom
    if os.path.exists('chapters_ro') and os.listdir('chapters_ro'):
        concatenate_manuscript('chapters_ro', 'doar_un_pic_mai_adanc_ro.md')
        check_romanian_headings('doar_un_pic_mai_adanc_ro.md')
        build_normal_pdf('chapters_ro', '../Doar_Un_Pic_Mai_Adanc_RO.pdf', 'ro_custom')

    # Romanian Eldoria
    if os.path.exists('chapters_ro_eldoria') and os.listdir('chapters_ro_eldoria'):
        concatenate_manuscript('chapters_ro_eldoria', 'pastratorii_inimii_din_eldoria_ro.md')
        check_romanian_headings('pastratorii_inimii_din_eldoria_ro.md')
        build_normal_pdf('chapters_ro_eldoria', '../Păstrătorii_Inimii_din_Eldoria_RO.pdf', 'ro_eldoria')
