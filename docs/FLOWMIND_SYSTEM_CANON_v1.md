# FLOWMIND SYSTEM CANON v1
Status: LOCKED
Mode: Deterministic Production Architecture
Change Policy: Immutable (changes only via explicit version upgrade)

------------------------------------------------------------
0. CORE PRINCIPLE
------------------------------------------------------------

Production does not make decisions.
Production executes a pre-approved manifest.

All decisions must be finalized BEFORE production starts.

No dynamic architecture changes during execution.
No self-modifying logic.
No layer mixing.

------------------------------------------------------------
ARCHITECTURE LAYERS (STRICT ORDER)
------------------------------------------------------------

LAYER -1 — VERIFIED DATA
Output: FACT_PACK.json
Contains:
- Verified numbers
- Sources
- Dates
- Links

No script generation allowed without FACT_PACK.

------------------------------------------------------------

LAYER 0 — TOPIC GATE
Output: TOPIC_CONTRACT.json
Requires:
- Ranking
- Justification
- Telegram approval

No production allowed without approval.

------------------------------------------------------------

LAYER 1 — SCRIPT ENGINE
Output:
- script.txt
- SCRIPT_META.json

Rules:
- Hook ≤ 15 seconds
- Structured conflict
- Numeric anchors
- Clear arc

------------------------------------------------------------

LAYER 2 — SCENE PLANNER
Output: SHOT_PLAN.json
Must contain per scene:
- start_time
- end_time
- visual_tags
- fx_tags
- mood
- transition_type

No visuals generated without SHOT_PLAN.

------------------------------------------------------------

LAYER 3 — ASSET ENGINE

3A — Stock Engine
- Pexels
- Pixabay
- Ranking
- Anti-repeat memory

3B — AI Fallback
- Used only if stock score < threshold

Output: ASSET_MAP.json

------------------------------------------------------------

LAYER 4 — AUDIO STACK
- Voice
- FX
- Music (mood-based)

Output:
- AUDIO_PLAN.json
- CUE_SHEET.json

------------------------------------------------------------

LAYER 5 — TIMELINE ORCHESTRATOR
Output: MASTER_TIMELINE.json
Combines:
- voice
- visuals
- fx
- music
- transitions

Audio = Master Clock

------------------------------------------------------------

LAYER 6 — PRODUCTION ASSEMBLY
- Render
- FFmpeg
- Basic QA

------------------------------------------------------------

LAYER 7 — DIRECTOR QA
Checks:
- Energy curve
- Silence detection
- Audio balance
- Visual brightness
- Repetition
- Style consistency

PASS or HALT only.

------------------------------------------------------------

LAYER 8 — THUMBNAIL ENGINE
- Emotional trigger logic
- Contrast validation
- Negative space
- A/B variants

------------------------------------------------------------

LAYER 9 — DELIVERY
- Telegram preview
- Manual approval
- Upload
- Archive
- Metrics capture

------------------------------------------------------------
STRICT RULES
------------------------------------------------------------

1. No layer skipping.
2. No parallel layer development.
3. No new features until current layer is complete.
4. No architecture change mid-layer.
5. Production cannot override Manifest.
6. Director cannot modify assets, only pass or halt.
7. Manifest is immutable after lock.

------------------------------------------------------------
DEVELOPMENT ORDER (MANDATORY)
------------------------------------------------------------

1. Verified Data Layer
2. Topic Gate
3. Scene Planner
4. Asset Engine
5. Audio Stack
6. Timeline Orchestrator
7. Director QA
8. Thumbnail Engine

Script Engine assumed baseline ready.

------------------------------------------------------------
CANON CHECK PROTOCOL
------------------------------------------------------------

Before every development step:
- State current layer
- Confirm previous layer complete
- Confirm no layer skipping
- Confirm no new architecture added

If violation detected → STOP.
