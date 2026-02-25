"""
FlowMind Cashflow — Delivery package (canonical)

Single entrypoint:
    from engine.delivery import run_delivery
"""

from .router import run_delivery  # noqa: F401
