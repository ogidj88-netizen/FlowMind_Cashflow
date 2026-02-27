# FACT PACK GATE RULES v1
Status: LOCKED
Layer: VERIFIED DATA
Purpose: Mandatory validation gate before Script Engine

------------------------------------------------------------
CORE RULE
------------------------------------------------------------

Script Engine MUST NOT start without a valid FACT_PACK.json.

If validation fails → HALT.

------------------------------------------------------------
VALIDATION CONDITIONS
------------------------------------------------------------

Before Script execution, system must verify:

1. FACT_PACK.json exists in project directory.
2. validation_status == "PASS"
3. confidence_score >= 0.75
4. Minimum 5 facts present.
5. All sources listed in DATA_SOURCES_REGISTRY.
6. Each fact contains:
   - numeric_value
   - source
   - publication_date
   - url

------------------------------------------------------------
FAIL BEHAVIOR
------------------------------------------------------------

If ANY condition fails:

- Script Engine must STOP.
- PROJECT_STATE.json:
    - halted = true
    - halt_reason = "FACT_PACK_VALIDATION_FAILED"
- No further layer execution allowed.

------------------------------------------------------------
SUCCESS BEHAVIOR
------------------------------------------------------------

If all conditions PASS:

- Script Engine may start.
- PROJECT_STATE.halted remains false.

------------------------------------------------------------
IMMUTABILITY RULE
------------------------------------------------------------

These rules are immutable under v1.
Changes require version upgrade.
