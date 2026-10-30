"""
CivicAI - AI Duplicate Detection Engine
Computes lexical, n-gram, and spatial-category similarity across
existing complaints to flag redundant submissions and merge triage.
"""
import re

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at",
    "to", "for", "with", "from", "by", "about", "near", "there", "it", "this",
    "that", "of", "please", "sir", "madam", "help", "kindly", "issue", "problem",
    "our", "my", "we", "they", "urgent", "very", "facing", "since", "days", "past",
    "front", "back", "side", "road", "street"
}

def stem(word):
    """Simple rule-based suffix trimmer for civic vocabulary."""
    w = word.lower()
    for suffix in ("ing", "es", "ed", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) > 3:
            return w[:-len(suffix)]
    return w

def get_tokens(text):
    if not text:
        return set()
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    words = cleaned.split()
    return {stem(w) for w in words if w not in STOPWORDS and len(w) > 2}

def get_raw_words(text):
    if not text:
        return []
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    return [stem(w) for w in cleaned.split() if w not in STOPWORDS and len(w) > 2]

def get_ngrams(text, n=2):
    words = get_raw_words(text)
    if len(words) < n:
        return set(words)
    return {' '.join(words[i:i+n]) for i in range(len(words)-n+1)}

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def detect_duplicate(description, category, location, existing_complaints, exclude_id=None):
    """
    Scans existing complaints to find duplicate reports.
    """
    desc_tokens = get_tokens(description)
    desc_bigrams = get_ngrams(description, 2)
    loc_tokens = get_tokens(location)

    best_match = None
    highest_score = 0.0
    match_keywords = []

    for comp in existing_complaints:
        comp_id = comp.get("id")
        if exclude_id and comp_id == exclude_id:
            continue

        existing_desc = comp.get("description", "")
        existing_loc = comp.get("location", "")
        existing_cat = comp.get("category", "")
        existing_status = comp.get("status", "")

        # Skip already resolved complaints
        if existing_status == "Resolved":
            continue

        ex_tokens = get_tokens(existing_desc)
        ex_bigrams = get_ngrams(existing_desc, 2)
        ex_loc_tokens = get_tokens(existing_loc)

        # 1. Token similarity (35%)
        token_sim = jaccard_similarity(desc_tokens, ex_tokens)

        # 2. Bigram phrase similarity (30%)
        bigram_sim = jaccard_similarity(desc_bigrams, ex_bigrams)

        # 3. Location token similarity (20%)
        loc_sim = jaccard_similarity(loc_tokens, ex_loc_tokens)

        # 4. Category match (15%)
        cat_match = 1.0 if category.lower() == existing_cat.lower() else 0.0

        # Direct token overlap count
        common = desc_tokens.intersection(ex_tokens)
        shared_count = len(common)

        # Base composite score
        score = (token_sim * 0.40) + (bigram_sim * 0.25) + (loc_sim * 0.25) + (cat_match * 0.10)

        # Spatial constraint: If both locations are explicitly given and have ZERO location overlap,
        # penalize duplicate score because the complaint is in a different neighborhood/ward
        if len(loc_tokens) > 0 and len(ex_loc_tokens) > 0 and loc_sim == 0.0:
            score *= 0.45

        # If significant core tokens match AND location tokens match
        if shared_count >= 3 and loc_sim >= 0.20:
            score = max(score, min(0.96, 0.50 + (shared_count * 0.08) + (loc_sim * 0.35)))

        if score > highest_score:
            highest_score = score
            best_match = comp
            match_keywords = list(common)[:4]

    similarity_percentage = round(highest_score * 100, 1)

    if highest_score >= 0.50 and best_match:
        track_id = best_match.get("tracking_id", f"#{best_match.get('id')}")
        words_str = ", ".join(f"'{w}'" for w in match_keywords) if match_keywords else "incident context"
        explanation = (
            f"High duplicate probability ({similarity_percentage}%) matching {track_id}. "
            f"Matching key terms: {words_str} with overlapping location profile. "
            f"Likely duplicate report from another citizen for the same municipal issue."
        )
        return {
            "is_duplicate": True,
            "duplicate_of_id": best_match.get("id"),
            "duplicate_tracking_id": track_id,
            "similarity_score": round(highest_score, 2),
            "explanation": explanation
        }
    elif highest_score >= 0.30 and best_match:
        track_id = best_match.get("tracking_id", f"#{best_match.get('id')}")
        return {
            "is_duplicate": False,
            "duplicate_of_id": None,
            "duplicate_tracking_id": track_id,
            "similarity_score": round(highest_score, 2),
            "explanation": f"Mild overlap ({similarity_percentage}%) with {track_id}, but represents a distinct incident or specific point."
        }
    else:
        return {
            "is_duplicate": False,
            "duplicate_of_id": None,
            "duplicate_tracking_id": None,
            "similarity_score": round(highest_score, 2),
            "explanation": "Unique complaint. No matching prior complaints found in this vicinity."
        }
