# FACT PACK CONTRACT v1
Status: LOCKED
Layer: VERIFIED DATA
Purpose: Deterministic factual input for Script Engine

------------------------------------------------------------
CORE PRINCIPLE
------------------------------------------------------------

FACT_PACK.json is mandatory before Script generation.

If FACT_PACK does not exist OR validation_status != PASS
→ Script Engine must halt.

------------------------------------------------------------
STRUCTURE (CANONICAL FORMAT)
------------------------------------------------------------

{
  "topic": "",
  "generated_at": "",
  "sources_used": [],
  "facts": [
    {
      "statement": "",
      "numeric_value": "",
      "unit": "",
      "context": "",
      "source": "",
      "publication_date": "",
      "url": "",
      "confidence": 0.0
    }
  ],
  "confidence_score": 0.0,
  "validation_status": "PASS | FAIL"
}

------------------------------------------------------------
FIELD REQUIREMENTS
------------------------------------------------------------

topic:
- Exact topic string used for generation.

generated_at:
- ISO timestamp.

sources_used:
- Unique list of sources referenced in facts.

facts:
- Minimum 5 entries.
- Each fact MUST contain:
  - numeric_value
  - source
  - publication_date
  - url

confidence:
- Range 0.0 – 1.0 per fact.

confidence_score:
- Aggregated average confidence.
- Threshold for PASS: >= 0.75

validation_status:
- PASS only if:
  - Minimum 5 valid facts
  - All sources in whitelist
  - All numeric anchors present
  - confidence_score >= 0.75
- Otherwise FAIL.

------------------------------------------------------------
STRICT RULES
------------------------------------------------------------

1. No opinion-based statements allowed.
2. No missing numeric_value.
3. No missing source.
4. No source outside DATA_SOURCES_REGISTRY.
5. No Script generation without PASS.

------------------------------------------------------------
IMMUTABILITY RULE
------------------------------------------------------------

This contract is immutable under v1.
Changes require version upgrade.
