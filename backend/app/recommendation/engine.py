import re
from typing import List, Dict, Any, Set, Tuple
from app.models.models import ExtractedRequirement, StandardCatalogue

# Curated technical synonym & concept expansion dictionary
CONCEPT_SYNONYMS: Dict[str, List[str]] = {
    "led": ["luminaire", "lighting", "solid state", "lamp", "illumination", "street light"],
    "luminaire": ["led", "lighting", "fixture", "street light", "lamp"],
    "street light": ["outdoor lighting", "roadway lighting", "luminaire", "led"],
    "ip66": ["ingress protection", "weatherproof", "dustproof", "waterproof", "outdoor", "enclosure"],
    "ip65": ["ingress protection", "weatherproof", "dustproof", "waterproof", "outdoor", "enclosure"],
    "surge": ["lightning", "transient", "overvoltage", "spd", "electrical protection"],
    "driver": ["power supply", "ballast", "controlgear", "constant current"],
    "photometric": ["lumen", "efficacy", "cri", "cct", "optical", "light distribution"],
    "die-cast": ["aluminium", "housing", "enclosure", "mechanical", "corrosion"],
    "earthing": ["grounding", "electrical safety", "insulation", "shock protection"],
    "cable": ["conductor", "wire", "insulation", "xlpe", "pvc", "armoured"],
    "pump": ["centrifugal", "submersible", "water supply", "motor", "hydraulic"],
    "pipe": ["hdpe", "pvc", "water distribution", "pressure", "plumbing"],
    "transformer": ["distribution", "power", "voltage", "winding", "insulation"],
    "medical": ["clinical", "hospital", "biomedical", "patient safety", "sterilization"],
    "helmet": ["ppe", "head protection", "impact", "safety gear"],
    "server": ["it equipment", "data center", "rack", "computing", "ups"],
    "cement": ["concrete", "construction", "structural", "aggregate", "masonry"],
    "warranty": ["quality assurance", "reliability", "batch testing", "inspection"],
}


def normalize_tokens(text: str) -> Set[str]:
    tokens = set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text.lower()))
    return {t for t in tokens if len(t) > 1}


def expand_concepts(tokens: Set[str]) -> Set[str]:
    expanded = set(tokens)
    for token in list(tokens):
        for key, syns in CONCEPT_SYNONYMS.items():
            if token == key or token in syns:
                expanded.add(key)
                expanded.update(syns)
    return expanded


def compute_recommendation(
    requirements: List[ExtractedRequirement],
    standard: StandardCatalogue,
    analysis_category: str = "",
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Compute transparent, explainable demo relevance score and requirement coverage.
    Returns: (recommendation_dict, requirement_mappings_list)
    """
    std_text = f"{standard.title} {standard.sector} {standard.product_category} {standard.description} {standard.scope} {' '.join(standard.technical_keywords or [])}"
    std_tokens = normalize_tokens(std_text)
    std_expanded = expand_concepts(std_tokens)
    std_cats = {c.lower() for c in (standard.related_requirement_categories or [])}

    addressed_codes: List[str] = []
    unaddressed_codes: List[str] = []
    matching_concepts: Set[str] = set()
    tender_evidence: List[str] = []
    mappings: List[Dict[str, Any]] = []

    req_scores: List[float] = []

    for req in requirements:
        req_text = f"{req.description} {' '.join(req.keywords or [])} {req.category}"
        req_tokens = normalize_tokens(req_text)
        req_expanded = expand_concepts(req_tokens)

        direct_overlap = req_tokens & std_tokens
        concept_overlap = req_expanded & std_expanded
        cat_match = req.category.lower() in std_cats

        # Per-requirement coverage score (0 to 1)
        lexical_ratio = len(direct_overlap) / max(len(req_tokens), 1)
        concept_ratio = len(concept_overlap) / max(len(req_expanded), 1)
        cov_score = min(1.0, lexical_ratio * 1.4 + concept_ratio * 0.9 + (0.25 if cat_match else 0.0))
        req_scores.append(cov_score)

        if cov_score >= 0.38:
            status = "covered"
            addressed_codes.append(req.req_code)
            matching_concepts.update(list(direct_overlap | (concept_overlap & std_tokens))[:5])
            tender_evidence.append(f"{req.req_code}: {req.description[:140]}")
        elif cov_score >= 0.22:
            status = "partially_covered"
            addressed_codes.append(req.req_code)
            matching_concepts.update(list(concept_overlap & std_tokens)[:3])
        elif cat_match:
            status = "needs_review"
            unaddressed_codes.append(req.req_code)
        else:
            status = "not_covered"
            unaddressed_codes.append(req.req_code)

        mappings.append({
            "requirement_id": req.id,
            "standard_id": standard.id,
            "coverage_status": status,
            "evidence_note": f"Matched concepts: {', '.join(sorted(list(direct_overlap | (concept_overlap & std_tokens)))[:5]) or 'Category alignment only'}",
            "confidence": round(cov_score, 2),
        })

    # Transparent 5-component ranking formula (0-100)
    category_rel = 20.0 if (analysis_category.lower() in standard.sector.lower() or analysis_category.lower() in standard.product_category.lower()) else 8.0
    avg_req_cov = (sum(req_scores) / max(len(req_scores), 1))
    keyword_overlap_score = min(25.0, len(matching_concepts) * 3.5)
    concept_sim_score = min(20.0, avg_req_cov * 28.0)
    scope_rel_score = 15.0 if len(addressed_codes) >= 2 else (8.0 if len(addressed_codes) == 1 else 2.0)
    coverage_score = min(20.0, (len(addressed_codes) / max(len(requirements), 1)) * 24.0)

    total_score = round(min(98.0, category_rel + keyword_overlap_score + concept_sim_score + scope_rel_score + coverage_score), 1)

    if total_score >= 70:
        match_label = "Best Match"
    elif total_score >= 50:
        match_label = "Partial Match"
    elif total_score >= 35:
        match_label = "Related Standard"
    else:
        match_label = "Requires Human Review"

    explanation = (
        f"{standard.catalogue_id} ({standard.title}) achieved a demo relevance score of {total_score}/100 "
        f"based on {len(addressed_codes)}/{len(requirements)} addressed requirements, "
        f"{len(matching_concepts)} matching technical concepts, and alignment with the {standard.sector} sector."
    )

    rec_dict = {
        "standard_id": standard.id,
        "relevance_score": total_score,
        "match_label": match_label,
        "score_breakdown": {
            "product_category_relevance": round(category_rel, 1),
            "keyword_overlap": round(keyword_overlap_score, 1),
            "technical_concept_similarity": round(concept_sim_score, 1),
            "scope_relevance": round(scope_rel_score, 1),
            "requirement_coverage": round(coverage_score, 1),
        },
        "explanation": explanation,
        "addressed_req_codes": addressed_codes,
        "unaddressed_req_codes": unaddressed_codes,
        "matching_concepts": sorted(list(matching_concepts))[:10],
        "tender_evidence": tender_evidence[:4],
        "catalogue_evidence": f"Scope: {standard.scope[:220]}",
        "uncertainty_notes": "Demo relevance score only — not a probability of compliance. Official BIS text, amendments, and QCO applicability are not verified in this demo catalogue.",
        "recommended_action": "Verify against official BIS portal and confirm applicability of all unaddressed requirements with a technical reviewer.",
    }
    return rec_dict, mappings
