# FlowMind Cashflow — Bash/Zsh RC (single source of truth)

export PATH="/home/admi/FlowMind_Cashflow/bin:$PATH"

# Stable helpers (no alias confusion)
fmqa()   { python3 /home/admi/FlowMind_Cashflow/fm.py qa   "$@"; }
fmst()   { python3 /home/admi/FlowMind_Cashflow/fm.py status "$@"; }
fmdone() { python3 /home/admi/FlowMind_Cashflow/fm.py done "$@"; }
fmpack() { /home/admi/FlowMind_Cashflow/bin/fmpack "$@"; }
