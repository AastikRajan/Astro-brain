"""
Vedic Astrology Computational Engine
=====================================
A Python-based system that reverse-engineers Vedic astrology into
deterministic, computable algorithms. Treats the system as a data pipeline:
    Raw astronomical data → Computed features → Interpretable insights

Architecture:
    core/       - Coordinate systems, divisional charts, houses, aspects
    strength/   - Shadbala, Bhavabala, Ashtakvarga, Vimshopak
    timing/     - Vimshottari, Yogini, Chara, KP sublords
    analysis/   - Yoga detection, Karakas, signification chains
    prediction/ - Main engine, confidence scoring
    data/       - JSON loader, chart data models
"""

__version__ = "0.1.0"
