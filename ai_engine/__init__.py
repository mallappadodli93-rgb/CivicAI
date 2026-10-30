"""
CivicAI - AI Engine Package
Unified, transparent, explainable NLP pipeline for civic complaints:
1. Categorization (Road Damage, Waterlogging, Garbage, Streetlight, Drainage, Other)
2. Short Executive Summary
3. Duplicate Detection (text similarity & location proximity)
4. Priority Scoring (High, Medium, Low) with explainable reasons
"""
from ai_engine.categorizer import categorize_complaint, VALID_CATEGORIES
from ai_engine.summarizer import summarize_complaint
from ai_engine.priority_scorer import calculate_priority
from ai_engine.duplicate_detector import detect_duplicate

def analyze_complaint(description, location="", category=None, existing_complaints=None, exclude_id=None):
    """
    Runs the full explainable CivicAI pipeline on a complaint.
    """
    # 1. Categorization
    cat_result = categorize_complaint(description, category)
    predicted_category = cat_result["category"]
    cat_confidence = cat_result["confidence"]

    # Use citizen category if explicitly selected from valid categories, otherwise auto-detected
    if category and category in VALID_CATEGORIES and category != "Auto-Detect":
        effective_category = category
    else:
        effective_category = predicted_category

    # 2. Short Executive Summary
    summary = summarize_complaint(description, effective_category, location)

    # 3. Priority Scoring (High, Medium, Low) with structured reasons
    priority_result = calculate_priority(description, effective_category, location)

    # 4. Duplicate Detection (text similarity & nearby location)
    if existing_complaints is None:
        existing_complaints = []

    dup_result = detect_duplicate(
        description=description,
        category=effective_category,
        location=location,
        existing_complaints=existing_complaints,
        exclude_id=exclude_id
    )

    return {
        "category": effective_category,
        "ai_category": predicted_category,
        "ai_category_confidence": cat_confidence,
        "category_explanation": cat_result["explanation"],
        "suggested_department": cat_result["suggested_department"],
        "ai_summary": summary,
        "ai_priority_level": priority_result["level"],
        "ai_priority_score": priority_result["score"],
        "ai_priority_reasons": priority_result["reasons"],
        "ai_priority_explanation": priority_result["explanation"],
        "is_duplicate": dup_result["is_duplicate"],
        "ai_duplicate_of": dup_result["duplicate_of_id"],
        "ai_duplicate_tracking_id": dup_result["duplicate_tracking_id"],
        "ai_duplicate_score": dup_result["similarity_score"],
        "ai_duplicate_notes": dup_result["explanation"]
    }
