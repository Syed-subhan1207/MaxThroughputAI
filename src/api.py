"""
Entry point wrapper for src/api.py delegating to backend/api.py orchestration hub.
Preserves existing import path for Person 3 execution.
"""

import os
import sys

# Ensure backend package is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.api import app, RailwayInput, home, predict, get_stations, get_analytics, get_live_data, get_optimization, get_system_status, get_dashboard_summary

__all__ = ["app", "RailwayInput"]