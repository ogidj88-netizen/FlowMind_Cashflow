# FlowMind Cashflow — Fish RC (single source of truth)

set -gx PATH /home/admi/FlowMind_Cashflow/bin $PATH

function fmqa
  python3 /home/admi/FlowMind_Cashflow/fm.py qa $argv
end

function fmst
  python3 /home/admi/FlowMind_Cashflow/fm.py status $argv
end

function fmdone
  python3 /home/admi/FlowMind_Cashflow/fm.py done $argv
end

function fmpack
  /home/admi/FlowMind_Cashflow/bin/fmpack $argv
end
