"""
Improved MCQ Extraction Script for Physiology PDF
Pattern:
- Red category headers
- First question directly below category
- Options listed below question
- Correct answer highlighted in yellow
- Answer number (e.g., 2, 3, 4) after options
- Next question appears after answer number
"""

import fitz  # PyMuPDF
import json
import re
from typing import List, Dict, Any, Tuple

def extract_mcqs_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract MCQs with proper category, question, options, and answers
    """
    doc = fitz.open(pdf_path)
    all_mcqs = []
    
    # Global state that persists across pages
    current_category = "General"
    current_question = ""
    current_options = []
    state = "LOOKING_FOR_QUESTION"
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text with position and formatting
        text_instances = page.get_text("dict")
        
        # Extract highlighted areas (yellow highlights)
        highlights = extract_highlights(page)
        
        # Process the page with persistent state
        page_mcqs, current_category, current_question, current_options, state = process_page_with_state(
            text_instances, highlights, page_num + 1,
            current_category, current_question, current_options, state
        )
        all_mcqs.extend(page_mcqs)
    
    # Save any remaining question
    if current_question and len(current_options) >= 2:
        mcq = create_mcq(current_category, current_question, current_options, len(doc))
        if mcq:
            all_mcqs.append(mcq)
    
    doc.close()
    return all_mcqs


def extract_highlights(page) -> List[Dict]:
    """
    Extract yellow highlighted text from page
    """
    highlights = []
    
    # Get all annotations
    annots = page.annots()
    if annots:
        for annot in annots:
            if annot.type[0] == 8:  # Highlight annotation
                # Get the color
                colors = annot.colors
                if colors and 'stroke' in colors:
                    # Yellow highlight typically has RGB close to (1, 1, 0)
                    r, g, b = colors['stroke']
                    if r > 0.9 and g > 0.9 and b < 0.5:  # Yellow-ish
                        rect = annot.rect
                        highlights.append({
                            'rect': rect,
                            'page': page.number
                        })
    
    return highlights


def process_page_with_state(text_dict: Dict, highlights: List[Dict], page_num: int,
                            current_category: str, current_question: str, 
                            current_options: List, state: str) -> Tuple[List[Dict], str, str, List, str]:
    """
    Process page while maintaining state across pages
    Returns: (mcqs_from_page, updated_category, updated_question, updated_options, updated_state)
    """
    mcqs = []
    
    # Extract all text elements in order
    text_elements = []
    for block in text_dict.get("blocks", []):
        if block.get('type') == 0:  # Text block
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '').strip()
                    if text:
                        color = span.get('color', 0)
                        # Convert to RGB
                        r = (color >> 16) & 0xFF
                        g = (color >> 8) & 0xFF
                        b = color & 0xFF
                        
                        text_elements.append({
                            'text': text,
                            'r': r, 'g': g, 'b': b,
                            'size': span.get('size', 0),
                            'bbox': span.get('bbox', None),
                            'y_pos': span.get('bbox', [0,0,0,0])[1]
                        })
    
    # Sort by vertical position
    text_elements.sort(key=lambda x: x['y_pos'])
    
    i = 0
    while i < len(text_elements):
        elem = text_elements[i]
        text = elem['text']
        r, g, b = elem['r'], elem['g'], elem['b']
        
        # CATEGORY: Red text (R=255, G=0, B=0)
        if r > 200 and g < 50 and b < 50:
            # Save previous question
            if current_question and len(current_options) >= 2:
                mcq = create_mcq(current_category, current_question, current_options, page_num)
                if mcq:
                    mcqs.append(mcq)
            
            current_category = text
            current_question = ""
            current_options = []
            state = "LOOKING_FOR_QUESTION"
            i += 1
            continue
        
        # LOOKING FOR QUESTION (after category or after answer number)
        if state == "LOOKING_FOR_QUESTION":
            # Question is any text that's not a single digit
            if not re.match(r'^[0-9]$', text):
                current_question = text
                current_options = []
                state = "COLLECTING_OPTIONS"
                i += 1
                continue
        
        # COLLECTING OPTIONS
        if state == "COLLECTING_OPTIONS":
            # Check if this is answer number (single digit 1-9)
            if re.match(r'^[1-9]$', text) and len(text) == 1:
                # Mark correct answer
                try:
                    answer_idx = int(text) - 1
                    if 0 <= answer_idx < len(current_options):
                        current_options[answer_idx]['is_correct'] = True
                except:
                    pass
                
                # Save question
                if current_question and len(current_options) >= 2:
                    mcq = create_mcq(current_category, current_question, current_options, page_num)
                    if mcq:
                        mcqs.append(mcq)
                
                # Reset for next question
                current_question = ""
                current_options = []
                state = "LOOKING_FOR_QUESTION"
                i += 1
                continue
            
            # Check if highlighted
            is_highlighted = is_text_highlighted_by_bbox(elem['bbox'], highlights)
            
            # Add as option (not red text, reasonable length)
            if r < 200 and len(text) > 0:
                current_options.append({
                    'text': text,
                    'is_correct': is_highlighted
                })
        
        i += 1
    
    return mcqs, current_category, current_question, current_options, state


def is_red_text(color: int) -> bool:
    """
    Check if text color is red
    RGB color is encoded as integer
    """
    # Extract RGB from integer
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    
    # Red text: high R, low G and B
    return r > 200 and g < 100 and b < 100


def is_text_highlighted_by_bbox(bbox, highlights: List[Dict]) -> bool:
    """
    Check if text bounding box overlaps with any highlight
    """
    if not bbox:
        return False
    
    for highlight in highlights:
        h_rect = highlight['rect']
        # Check if bounding boxes overlap
        if boxes_overlap(bbox, h_rect):
            return True
    
    return False


def boxes_overlap(box1, box2) -> bool:
    """
    Check if two bounding boxes overlap
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    return not (x1_max < x2_min or x2_max < x1_min or 
                y1_max < y2_min or y2_max < y1_min)


def create_mcq(category: str, question: str, options: List[Dict], page_num: int) -> Dict:
    """
    Create MCQ dictionary
    """
    if not question or len(options) < 2:
        return None
    
    # Find correct answer
    correct_idx = None
    for idx, opt in enumerate(options):
        if opt.get('is_correct', False):
            correct_idx = idx
            break
    
    return {
        'category': category if category else 'General',
        'question': question,
        'options': [opt['text'] for opt in options],
        'correct_answer': correct_idx,
        'page': page_num
    }


def save_to_json(mcqs: List[Dict], output_path: str):
    """
    Save MCQs to JSON file organized by category
    """
    # Organize by category
    organized = {}
    stats = {
        'total_mcqs': len(mcqs),
        'categories': {}
    }
    
    for mcq in mcqs:
        category = mcq['category']
        if category not in organized:
            organized[category] = []
            stats['categories'][category] = 0
        
        organized[category].append({
            'question': mcq['question'],
            'options': mcq['options'],
            'correct_answer': mcq['correct_answer'],
            'page': mcq['page']
        })
        stats['categories'][category] += 1
    
    # Save data
    output_data = {
        'stats': stats,
        'mcqs': organized
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"MCQ Extraction Complete!")
    print(f"{'='*60}")
    print(f"Total MCQs extracted: {len(mcqs)}")
    print(f"Total categories: {len(organized)}")
    print(f"\nCategory breakdown:")
    for cat, count in stats['categories'].items():
        print(f"  - {cat}: {count} questions")
    print(f"\nData saved to: {output_path}")


if __name__ == "__main__":
    pdf_path = "full physiology_260422_220102-1.pdf"
    output_path = "mcqs_data.json"
    
    print("="*60)
    print("MCQ Extraction Tool - Physiology Quiz")
    print("="*60)
    print(f"\nProcessing: {pdf_path}")
    print("This may take a few minutes for large PDFs...\n")
    
    try:
        mcqs = extract_mcqs_from_pdf(pdf_path)
        
        if mcqs:
            save_to_json(mcqs, output_path)
        else:
            print("\nWarning: No MCQs found!")
            print("Please check:")
            print("  1. PDF file path is correct")
            print("  2. PDF contains questions ending with '?'")
            print("  3. PDF has yellow highlights or answer numbers")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nPlease ensure PyMuPDF is installed:")
        print("  pip install PyMuPDF")
