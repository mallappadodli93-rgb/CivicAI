"""
CivicAI - Transparent Priority Scoring & Justification Engine
Evaluates complaints into High, Medium, or Low priority
and produces structured, explainable reasons matching municipal criteria.
"""
import re

# High-Severity Safety & Property Triggers
RESIDENTIAL_RISK_TRIGGERS = [
    "entering house", "entering homes", "entering residential", "flooding into house",
    "flooded home", "water entering", "flooding homes", "basement flood", "flooded basement",
    "property damage", "damage to house", "submerging houses", "compound wall collapsed",
    "structure damage", "water enters", "water entered"
]

SAFETY_HAZARD_TRIGGERS = [
    "open manhole", "manhole cover missing", "live wire", "hanging wire", "loose wire",
    "sparking", "electric shock", "deep sinkhole", "large sinkhole", "crater",
    "accident", "injured", "injury", "fell into", "risk to children", "near school",
    "near hospital", "pedestrian hazard", "collapse", "tree fallen", "contamination",
    "drinking water contaminated", "gas leak", "dog bite", "dangerous", "flooding",
    "road flooding", "street flooded"
]

IMMEDIATE_ATTENTION_TRIGGERS = [
    "immediate", "urgent", "emergency", "life threatening", "right now",
    "gushing continuously", "burst pipe", "flooding fast", "overflowing heavily",
    "since 4 days", "since 5 days", "since a week", "unattended", "entering house",
    "water entering", "open manhole", "live wire", "sparking", "sinkhole"
]

# Medium-Severity Inconvenience Triggers
MEDIUM_TRIGGERS = [
    "pothole", "streetlight not working", "dark street", "clogged drain", "drain blocked",
    "garbage pile", "uncollected trash", "dustbin overflow", "foul smell", "stench",
    "speed breaker damaged", "pipeline leak", "water puddle", "divider broken", "flickering light"
]

def calculate_priority(description, category="", location=""):
    """
    Computes priority level (High, Medium, Low) and generates bulleted justifications.
    """
    text = f"{description} {location}".lower()
    reasons = []

    # 1. Property Risk Assessment
    has_property_risk = any(re.search(r'\b' + re.escape(t), text) for t in RESIDENTIAL_RISK_TRIGGERS)
    if has_property_risk or (category == "Waterlogging" and ("house" in text or "home" in text or "entering" in text)):
        reasons.append("Risk to residential properties.")

    # 2. Public Safety Hazard Assessment
    has_safety_hazard = any(re.search(r'\b' + re.escape(t), text) for t in SAFETY_HAZARD_TRIGGERS)
    if has_safety_hazard or (category in ["Waterlogging", "Road Damage", "Drainage"] and ("flood" in text or "overflow" in text or "sinkhole" in text or "crater" in text)):
        reasons.append("Potential safety hazard.")

    # 3. Immediate Attention Assessment
    has_urgency = any(re.search(r'\b' + re.escape(t), text) for t in IMMEDIATE_ATTENTION_TRIGGERS)
    if has_urgency or (has_property_risk and has_safety_hazard):
        reasons.append("Immediate attention required.")

    # Classification
    if has_property_risk or (has_safety_hazard and len(reasons) >= 2) or "open manhole" in text or "live wire" in text or "sinkhole" in text:
        level = "High"
        score = 85
        # Ensure at least the core safety reasons are present for High priority
        if not reasons:
            reasons = [
                "Elevated public safety or property risk detected.",
                "Potential safety hazard.",
                "Immediate attention required."
            ]
        elif len(reasons) == 1:
            reasons.append("Potential safety hazard.")
            reasons.append("Immediate attention required.")
        elif len(reasons) == 2:
            reasons.append("Immediate attention required.")
    elif any(re.search(r'\b' + re.escape(t), text) for t in MEDIUM_TRIGGERS) or category in ["Garbage", "Streetlight", "Road Damage", "Drainage"]:
        level = "Medium"
        score = 50
        if category == "Garbage":
            reasons = [
                "Public sanitation and hygiene concern.",
                "Potential vector breeding and odor issue.",
                "Standard municipal sanitation clearance required."
            ]
        elif category == "Streetlight":
            reasons = [
                "Reduced night-time street visibility.",
                "Pedestrian and vehicular movement inconvenience.",
                "Electrical maintenance dispatch scheduled."
            ]
        elif category == "Road Damage":
            reasons = [
                "Surface unevenness affecting vehicular speed.",
                "Localized commuter inconvenience.",
                "Road patch repair recommended."
            ]
        elif category == "Drainage":
            reasons = [
                "Drainage slowdown and localized overflow.",
                "Risk of water stagnation if unaddressed.",
                "Drainage clearance team dispatch required."
            ]
        else:
            reasons = [
                "General municipal maintenance requirement.",
                "Non-life-threatening civic inconvenience.",
                "Scheduled for standard departmental action."
            ]
    else:
        level = "Low"
        score = 20
        reasons = [
            "Minor aesthetic or non-urgent maintenance issue.",
            "No direct threat to life, property, or traffic.",
            "Scheduled for routine municipal service cycle."
        ]

    # Format human-readable bulleted explanation
    explanation = "\n".join(f"- {r}" for r in reasons)

    return {
        "level": level,
        "score": score,
        "reasons": reasons,
        "explanation": explanation
    }
