"""
SCRIPT_CONSTITUTION_CASHFLOW_v1
STATUS: CANONICAL — DO NOT MODIFY WITHOUT VERSION UPDATE

Applies to:
- Money Mistakes
- Invisible Costs
- Cashflow Mode long-form (7–9 min)
"""

CONSTITUTION = {
    "core_principle": "Every scene must show financial loss, explain loss mechanism, or show how to stop loss.",

    "hook_rules": {
        "max_seconds": 15,
        "must_include_number": True,
        "forbidden_phrases": [
            "hi guys",
            "welcome back",
        ],
    },

    "structure_order": [
        "hook",
        "context_with_number",
        "mechanism",
        "peak",
        "second_impact",
        "practical_control",
        "bridge",
    ],

    "rhythm": {
        "max_words_per_sentence": 20,
        "max_paragraph_lines": 4,
    },

    "humor_required": True,

    "ymyl_forbidden": [
        "guaranteed",
        "risk free",
        "you will get rich",
    ],

    "min_sources": 1,
    "max_sources": 3,
}
