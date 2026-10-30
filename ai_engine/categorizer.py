"""
CivicAI - Transparent Rule-based & NLP Categorization Engine
Maps complaint text into the 6 designated civic categories:
- Road Damage
- Waterlogging
- Garbage
- Streetlight
- Drainage
- Other
"""
import re

CATEGORIES = {
    "Road Damage": {
        "keywords": [
            ("pothole", 4.0), ("sinkhole", 4.0), ("crater", 3.5), ("caved in", 3.5),
            ("asphalt", 3.0), ("tar road", 3.0), ("broken road", 3.5), ("damaged road", 3.5),
            ("broken footpath", 3.5), ("broken sidewalk", 3.5), ("footpath damaged", 3.5),
            ("speed breaker", 3.0), ("cracked road", 3.0), ("uneven road", 2.5),
            ("road surface", 2.5), ("road damage", 3.5), ("footpath", 1.0), ("sidewalk", 1.0), ("road", 0.5)
        ],
        "department": "Department of Roads & Infrastructure"
    },
    "Waterlogging": {
        "keywords": [
            ("waterlogging", 4.5), ("water logging", 4.5), ("flooding", 4.0), ("flood", 4.0),
            ("water entering", 4.0), ("water entered", 4.0), ("submerged", 3.5), ("stagnant water", 3.5),
            ("standing water", 3.5), ("road flooding", 4.0), ("street flooded", 4.0),
            ("inundated", 4.0), ("water accumulated", 3.5), ("gushing water", 3.0),
            ("waterlogged", 4.5), ("knee deep water", 4.0)
        ],
        "department": "Stormwater & Flood Management Division"
    },
    "Garbage": {
        "keywords": [
            ("garbage", 4.0), ("trash", 4.0), ("waste", 3.5), ("dump", 3.5),
            ("dumping", 3.5), ("dustbin", 3.5), ("bin overflow", 4.0), ("uncollected garbage", 4.0),
            ("stench", 3.5), ("foul smell", 3.5), ("smell", 2.5), ("litter", 3.0),
            ("debris", 3.0), ("dead animal", 4.0), ("filth", 3.0), ("solid waste", 3.5),
            ("rubbish", 3.5)
        ],
        "department": "Solid Waste & Sanitation Department"
    },
    "Streetlight": {
        "keywords": [
            ("streetlight", 4.5), ("street light", 4.5), ("lamp post", 4.0), ("street lamp", 4.0),
            ("dark street", 3.5), ("pitch dark", 3.5), ("light not working", 4.0), ("broken light", 3.5),
            ("flickering light", 3.5), ("no light on street", 4.0), ("dark at night", 3.0),
            ("pole sparking", 3.5), ("loose wire on pole", 3.5), ("hanging wire", 3.0),
            ("live wire", 4.0), ("electrical wire", 4.0), ("electric wire", 4.0), ("sparking wire", 4.0),
            ("electric pole", 4.0), ("sparking", 3.0), ("electrocution", 4.0), ("fuse box", 3.5)
        ],
        "department": "Public Lighting & Electrical Works"
    },
    "Drainage": {
        "keywords": [
            ("drainage", 4.0), ("drain", 3.5), ("sewage", 4.0), ("sewer", 4.0),
            ("gutter", 3.5), ("open manhole", 4.0), ("manhole cover", 4.0), ("manhole overflow", 4.5),
            ("clogged drain", 4.0), ("blocked drain", 4.0), ("sewer overflow", 4.5),
            ("dirty water leak", 3.5), ("stormwater drain", 3.5), ("burst pipe", 3.5),
            ("pipeline leak", 3.5), ("foul sewage", 4.0)
        ],
        "department": "Water Supply & Sewerage Board"
    }
}

VALID_CATEGORIES = list(CATEGORIES.keys()) + ["Other"]

def clean_text(text):
    return (text or "").lower()

def categorize_complaint(text, provided_category=None):
    """
    Analyzes complaint text with stemmed keyword matching and domain weighting.
    Returns category, confidence score, explanation, and matched keywords.
    """
    cleaned = clean_text(text)
    scores = {}
    matched_terms = {}

    for cat_name, cat_data in CATEGORIES.items():
        score = 0.0
        matches = []
        for kw, weight in cat_data["keywords"]:
            # Stemmed prefix matching: e.g. "flood" matches "flooding", "flooded"
            pattern = r'\b' + re.escape(kw)
            occurrences = len(re.findall(pattern, cleaned))
            if occurrences > 0:
                score += occurrences * weight
                matches.append(kw)
        scores[cat_name] = score
        matched_terms[cat_name] = matches

    # Determine best scoring category
    best_category = max(scores, key=scores.get)
    max_score = scores[best_category]
    total_score = sum(scores.values())

    if max_score >= 3.0:
        confidence = min(0.98, round((max_score / (total_score + 0.5)) * 0.5 + 0.45, 2))
    elif provided_category and provided_category in VALID_CATEGORIES and provided_category != "Auto-Detect":
        best_category = provided_category
        confidence = 0.70
    elif max_score >= 1.5:
        confidence = 0.55
    else:
        best_category = "Other"
        confidence = 0.40

    matches = matched_terms.get(best_category, [])
    if matches:
        terms_str = ", ".join(f"'{m}'" for m in matches[:3])
        explanation = f"Classified under {best_category} based on keywords: {terms_str}."
    else:
        explanation = f"Classified under {best_category} based on overall description context."

    dept = CATEGORIES.get(best_category, {}).get("department", "General Municipal Administration")

    return {
        "category": best_category,
        "confidence": confidence,
        "explanation": explanation,
        "suggested_department": dept,
        "matched_keywords": matches
    }
