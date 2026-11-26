import re
from typing import List, Dict, Any

CATEGORY_RULES = [
    ("Safety", ["safety", "shock", "insulation", "earthing", "grounding", "fire", "overload", "short circuit", "surge", "hazard", "protection class"]),
    ("Electrical", ["voltage", "watt", "wattage", "power factor", "frequency", "hz", "ampere", "current", "driver", "thd", "harmonic", "ac", "dc", "kv"]),
    ("Environmental", ["ip65", "ip66", "ip67", "ip68", "ingress", "weatherproof", "dust", "waterproof", "humidity", "temperature", "corrosion", "uv", "outdoor", "ambient"]),
    ("Performance", ["lumen", "efficacy", "lm/w", "cri", "cct", "kelvin", "efficiency", "flow rate", "pressure", "throughput", "capacity", "lifespan", "hours"]),
    ("Testing", ["test", "testing", "type test", "routine test", "acceptance test", "photometric", "thermal", "vibration", "impact", "ik08", "ik10", "lab"]),
    ("Certification", ["certif", "bis", "isi", "qco", "nabl", "iso", "compliance", "marking", "license", "accredited"]),
    ("Material", ["aluminium", "aluminum", "steel", "die-cast", "polycarbonate", "copper", "stainless", "alloy", "galvanized", "pvc", "hdpe"]),
    ("Mechanical", ["mounting", "bracket", "enclosure", "housing", "dimension", "weight", "torque", "wind load", "ik", "vibration"]),
    ("Quality assurance", ["warranty", "quality", "inspection", "sampling", "audit", "batch", "traceability", "documentation"]),
    ("Product specification", ["luminaire", "led", "street light", "cable", "transformer", "pump", "pipe", "meter", "helmet", "server", "equipment"]),
]

UNIT_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:W|kW|V|kV|A|mA|Hz|lm|lm/W|K|°C|C|hours|hrs|mm|cm|m|kg|bar|psi|%|dB)|IP\d{2}|IK\d{2})\b",
    re.IGNORECASE,
)

CRITICAL_MARKERS = ["shall", "must", "mandatory", "critical", "compulsory", "required", "minimum", "ip66", "ip65", "surge", "safety"]


def _detect_category(sentence: str) -> str:
    lower = sentence.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return category
    return "Product specification"


def _extract_keywords(sentence: str) -> List[str]:
    lower = sentence.lower()
    found = []
    for _, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in lower and kw not in found:
                found.append(kw)
    return found[:8]


def _detect_criticality(sentence: str) -> str:
    lower = sentence.lower()
    if any(m in lower for m in ["mandatory", "critical", "safety", "surge", "ip66", "ip65", "shock"]):
        return "critical"
    if any(m in lower for m in ["shall", "must", "minimum", "required"]):
        return "high"
    return "standard"


def extract_requirements_from_text(text: str, source_document: str = "Tender Document") -> List[Dict[str, Any]]:
    """
    Deterministic rule-based requirement extractor.
    Extracts structured requirements with source spans without inventing numeric values.
    """
    if not text or not text.strip():
        return []

    current_page = "Page 1"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates: List[Dict[str, Any]] = []

    for line in lines:
        page_match = re.match(r"^\[Page\s+(\d+)\]$", line, re.IGNORECASE)
        if page_match:
            current_page = f"Page {page_match.group(1)}"
            continue

        # Split long paragraphs into sentences if needed
        parts = re.split(r"(?<=[.;])\s+", line) if len(line) > 180 else [line]
        for part in parts:
            cleaned = re.sub(r"^[\-\*\d\.\)\s]+", "", part).strip()
            if len(cleaned) < 20:
                continue

            lower = cleaned.lower()
            is_req = (
                any(w in lower for w in ["shall", "must", "should", "required", "minimum", "maximum", "ip", "watt", "volt", "test", "certif", "warranty", "material", "housing", "luminaire", "led", "outdoor"])
                or bool(UNIT_PATTERN.search(cleaned))
            )
            if not is_req:
                continue

            units = UNIT_PATTERN.findall(cleaned)
            units_str = ", ".join(dict.fromkeys(units)) if units else None
            category = _detect_category(cleaned)
            keywords = _extract_keywords(cleaned)
            criticality = _detect_criticality(cleaned)

            candidates.append({
                "description": cleaned,
                "category": category,
                "keywords": keywords,
                "units_or_conditions": units_str,
                "criticality": criticality,
                "source_document": source_document,
                "source_location": current_page,
                "evidence_text": cleaned,
                "confidence": 0.88 if units_str or keywords else 0.74,
                "review_status": "extracted",
                "is_confirmed": False,
            })

    # Deduplicate and cap at 25 for clean UI
    seen = set()
    unique: List[Dict[str, Any]] = []
    for item in candidates:
        key = item["description"].lower()[:80]
        if key not in seen:
            seen.add(key)
            item["req_code"] = f"REQ-{len(unique) + 1:03d}"
            unique.append(item)
        if len(unique) >= 25:
            break

    return unique
