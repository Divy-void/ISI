from sqlalchemy.orm import Session
from app.models.models import Department, User, StandardCatalogue, AuditEvent

SAMPLE_TENDER_TEXT = """[Page 1]
MUNICIPAL CORPORATION PROCUREMENT TENDER (SYNTHETIC DEMONSTRATION)
Title: Supply, Installation and Testing of Outdoor LED Street Lighting Luminaires
Department: Municipal Electrical & Street Lighting Division

1. Product Specification:
1.1 The luminaire shall be an outdoor LED street light fixture suitable for municipal roadway illumination with die-cast aluminium housing.
1.2 The luminaire shall operate at nominal 230V AC, 50 Hz single-phase supply with wide operating voltage range of 140V to 270V AC.

2. Lighting Performance:
2.1 System luminous efficacy shall be minimum 120 lm/W with correlated colour temperature (CCT) of 5700K and CRI >= 70.
2.2 The LED driver shall be constant current type with power factor >= 0.95 and Total Harmonic Distortion (THD) <= 10%.

3. Electrical Safety & Surge Protection:
3.1 The luminaire shall include internal and external surge protection of minimum 10 kV / 10 kA against lightning and transient overvoltages.
3.2 Proper earthing terminal and Class I electrical insulation shall be provided to prevent electric shock hazards.

4. Environmental Protection & Mechanical Durability:
4.1 The complete luminaire enclosure shall have minimum IP66 ingress protection against dust and heavy rain for outdoor weatherproof operation.
4.2 The optical cover shall be toughened glass or UV-stabilized polycarbonate with minimum IK08 impact resistance.

5. Testing, Certification & Quality Assurance:
5.1 Type test reports from NABL-accredited or equivalent recognized laboratory shall be submitted for photometric, thermal, IP66, and surge tests.
5.2 The supplier shall provide a minimum 5-year comprehensive warranty and batch inspection documentation.
"""

DEMO_STANDARDS = [
    {
        "catalogue_id": "DEMO-STD-001",
        "title": "Illustrative Standard for Outdoor LED Street Lighting Luminaires",
        "sector": "Lighting",
        "product_category": "Outdoor Luminaires",
        "description": "Synthetic demonstration specification covering safety, photometric performance, and weatherproof construction of LED street lights.",
        "scope": "Applies to road and street lighting LED luminaires operating up to 250V AC for municipal and highway applications.",
        "technical_keywords": ["led", "luminaire", "street light", "outdoor", "ip66", "lumen", "efficacy", "die-cast", "photometric", "cct", "cri"],
        "related_requirement_categories": ["Product specification", "Performance", "Environmental", "Mechanical"],
        "applicability_conditions": "Applicable to pole-mounted outdoor LED street lighting fixtures.",
    },
    {
        "catalogue_id": "DEMO-STD-002",
        "title": "Illustrative Standard for Electronic LED Controlgear and Drivers",
        "sector": "Lighting",
        "product_category": "LED Drivers",
        "description": "Synthetic demonstration specification for constant-current AC/DC electronic controlgear used in LED luminaires.",
        "scope": "Covers power factor, THD, thermal protection, and electrical safety of LED drivers up to 250V.",
        "technical_keywords": ["driver", "controlgear", "power factor", "thd", "harmonic", "voltage", "230v", "50 hz", "constant current"],
        "related_requirement_categories": ["Electrical", "Performance", "Safety"],
        "applicability_conditions": "Applicable to built-in or independent LED drivers.",
    },
    {
        "catalogue_id": "DEMO-STD-003",
        "title": "Illustrative Standard for Surge Protection Devices in Outdoor Lighting",
        "sector": "Electrical equipment",
        "product_category": "Surge Protection",
        "description": "Synthetic demonstration specification for lightning and transient overvoltage protection in low-voltage outdoor installations.",
        "scope": "Covers 10 kV / 10 kA surge protective devices, earthing coordination, and impulse withstand testing.",
        "technical_keywords": ["surge", "lightning", "transient", "overvoltage", "10 kv", "earthing", "grounding", "insulation", "shock"],
        "related_requirement_categories": ["Safety", "Electrical", "Testing"],
        "applicability_conditions": "Required for outdoor electrical equipment exposed to lightning transients.",
    },
    {
        "catalogue_id": "DEMO-STD-004",
        "title": "Illustrative Standard for Degrees of Ingress Protection (IP Code) & Impact (IK)",
        "sector": "Safety and testing",
        "product_category": "Enclosure Protection",
        "description": "Synthetic demonstration classification for dust, water, and mechanical impact protection of electrical enclosures.",
        "scope": "Defines test methods for IP65, IP66, IP67, IP68 weatherproof ratings and IK08/IK10 impact resistance.",
        "technical_keywords": ["ip66", "ip65", "ingress", "weatherproof", "dust", "waterproof", "ik08", "impact", "enclosure", "testing"],
        "related_requirement_categories": ["Environmental", "Testing", "Mechanical"],
        "applicability_conditions": "Applicable to outdoor electrical and lighting enclosures.",
    },
    {
        "catalogue_id": "DEMO-STD-005",
        "title": "Illustrative Standard for Photometric & Laboratory Type Testing of Luminaires",
        "sector": "Safety and testing",
        "product_category": "Photometric Testing",
        "description": "Synthetic demonstration protocol for NABL-accredited laboratory type testing, thermal endurance, and warranty verification.",
        "scope": "Covers goniophotometry, lumen maintenance, thermal rise, and batch acceptance testing.",
        "technical_keywords": ["photometric", "type test", "nabl", "lab", "thermal", "warranty", "batch", "inspection", "quality"],
        "related_requirement_categories": ["Testing", "Certification", "Quality assurance"],
        "applicability_conditions": "Applicable to tender acceptance and type-test verification.",
    },
    {
        "catalogue_id": "DEMO-STD-006",
        "title": "Illustrative Standard for XLPE Insulated Armoured Power Cables",
        "sector": "Electrical equipment",
        "product_category": "Power Cables",
        "description": "Synthetic demonstration specification for 1.1 kV grade XLPE insulated, PVC sheathed armoured underground cables.",
        "scope": "Covers copper/aluminium conductors, insulation thickness, armouring, and routine high-voltage tests.",
        "technical_keywords": ["cable", "xlpe", "conductor", "armoured", "copper", "aluminium", "insulation", "voltage"],
        "related_requirement_categories": ["Electrical", "Material", "Safety"],
        "applicability_conditions": "Applicable to underground power distribution and street lighting feeders.",
    },
    {
        "catalogue_id": "DEMO-STD-007",
        "title": "Illustrative Standard for Oil-Immersed Distribution Transformers",
        "sector": "Electrical equipment",
        "product_category": "Transformers",
        "description": "Synthetic demonstration specification for 11 kV / 433 V three-phase distribution transformers.",
        "scope": "Covers core losses, winding temperature rise, dielectric strength, and energy efficiency levels.",
        "technical_keywords": ["transformer", "distribution", "winding", "voltage", "efficiency", "insulation", "kv"],
        "related_requirement_categories": ["Electrical", "Performance", "Testing"],
        "applicability_conditions": "Applicable to utility and municipal power distribution.",
    },
    {
        "catalogue_id": "DEMO-STD-008",
        "title": "Illustrative Standard for Submersible Centrifugal Water Pumps",
        "sector": "Water systems",
        "product_category": "Water Pumps",
        "description": "Synthetic demonstration specification for borewell and municipal water supply submersible pump sets.",
        "scope": "Covers hydraulic head, flow rate, motor efficiency, and stainless steel impeller construction.",
        "technical_keywords": ["pump", "submersible", "centrifugal", "water", "flow rate", "motor", "stainless", "hydraulic"],
        "related_requirement_categories": ["Product specification", "Performance", "Material"],
        "applicability_conditions": "Applicable to municipal water supply and irrigation.",
    },
    {
        "catalogue_id": "DEMO-STD-009",
        "title": "Illustrative Standard for HDPE Pipes for Potable Water Supply",
        "sector": "Water systems",
        "product_category": "Water Pipes",
        "description": "Synthetic demonstration specification for high-density polyethylene (HDPE) pressure pipes.",
        "scope": "Covers pressure ratings, hydrostatic strength, UV resistance, and potable water safety.",
        "technical_keywords": ["pipe", "hdpe", "water", "pressure", "uv", "potable", "corrosion"],
        "related_requirement_categories": ["Material", "Environmental", "Testing"],
        "applicability_conditions": "Applicable to underground municipal water distribution.",
    },
    {
        "catalogue_id": "DEMO-STD-010",
        "title": "Illustrative Standard for Industrial Safety Helmets (PPE)",
        "sector": "Safety and testing",
        "product_category": "Personal Protective Equipment",
        "description": "Synthetic demonstration specification for protective helmets used in construction and electrical maintenance.",
        "scope": "Covers shock absorption, penetration resistance, chin strap strength, and electrical insulation.",
        "technical_keywords": ["helmet", "ppe", "impact", "safety", "shock", "insulation", "polycarbonate"],
        "related_requirement_categories": ["Safety", "Mechanical", "Testing"],
        "applicability_conditions": "Applicable to industrial and utility field workers.",
    },
    {
        "catalogue_id": "DEMO-STD-011",
        "title": "Illustrative Standard for Structural Portland Cement & Concrete",
        "sector": "Construction",
        "product_category": "Cement & Concrete",
        "description": "Synthetic demonstration specification for ordinary Portland cement used in civil and municipal infrastructure.",
        "scope": "Covers compressive strength, setting time, chemical composition, and batch sampling.",
        "technical_keywords": ["cement", "concrete", "construction", "structural", "strength", "sampling"],
        "related_requirement_categories": ["Material", "Quality assurance", "Testing"],
        "applicability_conditions": "Applicable to public works and structural foundations.",
    },
    {
        "catalogue_id": "DEMO-STD-012",
        "title": "Illustrative Standard for Hospital Patient Monitoring Equipment",
        "sector": "Medical equipment",
        "product_category": "Clinical Devices",
        "description": "Synthetic demonstration specification for multi-parameter patient monitors in public hospitals.",
        "scope": "Covers electrical leakage limits, alarm accuracy, electromagnetic compatibility, and clinical safety.",
        "technical_keywords": ["medical", "hospital", "patient", "clinical", "safety", "alarm", "leakage"],
        "related_requirement_categories": ["Safety", "Electrical", "Certification"],
        "applicability_conditions": "Applicable to ICU and ward patient monitoring procurements.",
    },
    {
        "catalogue_id": "DEMO-STD-013",
        "title": "Illustrative Standard for Enterprise Rack Servers & Data Center UPS",
        "sector": "IT equipment",
        "product_category": "Servers & UPS",
        "description": "Synthetic demonstration specification for rack-mounted servers and online double-conversion UPS systems.",
        "scope": "Covers power efficiency, thermal operating range, harmonic distortion, and electromagnetic safety.",
        "technical_keywords": ["server", "it equipment", "ups", "rack", "data center", "efficiency", "thd"],
        "related_requirement_categories": ["Product specification", "Electrical", "Performance"],
        "applicability_conditions": "Applicable to e-governance data centers.",
    },
    {
        "catalogue_id": "DEMO-STD-014",
        "title": "Illustrative Standard for Hot-Dip Galvanized Steel Poles",
        "sector": "Mechanical equipment",
        "product_category": "Lighting Poles",
        "description": "Synthetic demonstration specification for octagonal galvanized steel street light poles.",
        "scope": "Covers wind load resistance, zinc coating thickness, base plate dimensions, and corrosion protection.",
        "technical_keywords": ["pole", "steel", "galvanized", "wind load", "mounting", "corrosion", "outdoor"],
        "related_requirement_categories": ["Mechanical", "Material", "Environmental"],
        "applicability_conditions": "Applicable to outdoor street lighting installations.",
    },
]


def seed_database(db: Session) -> None:
    if db.query(User).count() == 0:
        depts = [
            Department(name="Municipal Electrical & Lighting", code="ELEC"),
            Department(name="Public Works & Infrastructure", code="PWD"),
            Department(name="Central Procurement Cell", code="CPC"),
        ]
        db.add_all(depts)
        db.flush()

        users = [
            User(
                username="officer.demo",
                full_name="Aarav Sharma (Procurement Officer)",
                email="officer.demo@is-assist.local",
                role="procurement_officer",
                department_id=depts[0].id,
            ),
            User(
                username="reviewer.demo",
                full_name="Priya Nair (Technical Reviewer)",
                email="reviewer.demo@is-assist.local",
                role="technical_reviewer",
                department_id=depts[1].id,
            ),
            User(
                username="admin.demo",
                full_name="Vikram Rao (System Administrator)",
                email="admin.demo@is-assist.local",
                role="admin",
                department_id=depts[2].id,
            ),
        ]
        db.add_all(users)
        db.flush()

        db.add(AuditEvent(
            user_id=users[2].id,
            username="system",
            action="SEED_DATABASE",
            entity_type="system",
            entity_id="init",
            details="Seeded demonstration users, departments, and synthetic standards catalogue.",
        ))

    if db.query(StandardCatalogue).count() == 0:
        for item in DEMO_STANDARDS:
            db.add(StandardCatalogue(**item))

    db.commit()
