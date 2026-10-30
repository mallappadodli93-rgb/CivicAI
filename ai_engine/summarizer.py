"""
CivicAI - AI Summarizer Engine
Generates concise, factual executive summaries of civic complaints
by extracting root issues, impact zones, and urgency.
"""
import re

ABBREVIATIONS = ["st.", "dr.", "rd.", "ave.", "no.", "mr.", "mrs.", "ms.", "opp.", "nr."]

def clean_and_split_sentences(text):
    # Temporarily protect common abbreviations from sentence splitting
    placeholder_text = text
    for i, abbr in enumerate(ABBREVIATIONS):
        placeholder = f"__ABBR_{i}__"
        placeholder_text = re.sub(re.escape(abbr), placeholder, placeholder_text, flags=re.IGNORECASE)

    # Split on sentence boundaries
    raw_sentences = [s.strip() for s in re.split(r'[.!?\n]+', placeholder_text) if len(s.strip()) > 6]
    
    # Restore abbreviations
    restored_sentences = []
    for s in raw_sentences:
        for i, abbr in enumerate(ABBREVIATIONS):
            placeholder = f"__ABBR_{i}__"
            s = s.replace(placeholder, abbr.capitalize() if abbr.startswith("st.") or abbr.startswith("dr.") else abbr)
        restored_sentences.append(s)
        
    return restored_sentences

def summarize_complaint(text, category="Civic Issue", location=""):
    """
    Transforms citizen descriptions into a structured, concise executive summary.
    """
    if not text:
        return "No complaint description provided."

    text_clean = re.sub(r'\s+', ' ', text.strip())
    sentences = clean_and_split_sentences(text_clean)

    # Keyword indicators of core civic problems
    problem_indicators = [
        "pothole", "burst", "leak", "overflow", "blackout", "sparking", "garbage",
        "trash", "manhole", "danger", "flooding", "collapsed", "broken", "dirty water",
        "stray dog", "smell", "uncollected", "power cut", "damaged", "hazard", "wire"
    ]

    selected = []
    for s in sentences:
        s_lower = s.lower()
        if any(term in s_lower for term in problem_indicators):
            selected.append(s)
            if len(selected) >= 2:
                break

    if not selected:
        selected = sentences[:2] if sentences else [text_clean[:140]]

    core_summary = ". ".join(selected)
    if not core_summary.endswith('.'):
        core_summary += '.'

    # Check if location context is already present
    loc_mention = False
    if location:
        loc_words = [w.lower() for w in re.sub(r'[^a-zA-Z0-9\s]', '', location).split() if len(w) > 3]
        if any(w in core_summary.lower() for w in loc_words):
            loc_mention = True

    if not loc_mention and location and location.lower() != 'unspecified':
        prefix = f"[{category} | {location}] "
        core_summary = prefix + core_summary

    if len(core_summary) > 220:
        core_summary = core_summary[:217] + "..."

    return core_summary
