#!/usr/bin/env python3
"""
FlowMind Cashflow — Delivery Router v1
"""

from engine.delivery.final_qa import run_final_qa


def run_delivery(project_id: str) -> dict:
    return run_final_qa(project_id)
