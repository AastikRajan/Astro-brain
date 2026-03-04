# Module: main.py
## Last Updated: 2026-03-02

## PURPOSE
CLI entry point for the Vedic astrology engine. Parses command-line arguments, loads or builds the birth chart, runs the full prediction pipeline, and renders a human-readable report to stdout. Optionally invokes the GPT-4o interpreter for narrative synthesis. Handles UTF-8 output encoding for Windows compatibility.

## KEY FUNCTIONS

### main() → None
- **Purpose:** CLI main — orchestrates the full run
- **Inputs:** sys.argv (chart_file, date, domain, --ai flags)
- **Returns:** prints report to stdout
- **Called by:** `__main__` block
- **Calls:** `load_sample_chart()` or `build_chart_swe()`, `PredictionEngine.analyze_static()`, `PredictionEngine.predict()`, `print_static_summary()`, `print_domain_report()`

### print_static_summary(static) → None
- **Purpose:** Render natal chart section (positions, dignities, shadbala, yogas, dashas)
- **Inputs:** static_data dict from analyze_static()
- **Called by:** `main()`

### print_domain_report(report, domain) → None
- **Purpose:** Render domain-specific prediction section with confidence, windows, timing
- **Inputs:** prediction report dict
- **Called by:** `main()`

### banner(title, width) → str
- **Purpose:** ASCII banner renderer for section headers
### section(title) → str
- **Purpose:** Thinner section divider renderer

## IMPORTANT CONSTANTS
- `SIGN_NAMES` — 12 sign display strings
- `PLANET_SYMBOLS` — planet → 2-char symbol dict
- `_AI_MODULE_AVAILABLE` — feature flag for GPT interpreter

## DEPENDENCIES
engine.py, loader.py, interpreter.py (optional, via try/import)

## RECENT CHANGES
- 2026-03-02: Added UTF-8 reconfigure for Windows stdout compatibility
- 2026-03-02: Added --ai flag and VedicInterpreter integration
