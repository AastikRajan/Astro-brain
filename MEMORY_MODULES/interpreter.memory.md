# Module: interpreter.py
## Last Updated: 2026-03-02

## PURPOSE
GPT-4o based narrative interpreter for the Vedic astrology prediction output. Takes the structured engine output dict and generates a human-readable narrative interpretation using the OpenAI API. Activated via --ai flag in main.py. Requires OPENAI_API_KEY environment variable.

## KEY FUNCTIONS

### VedicInterpreter.interpret(prediction_report, domain, verbosity) → str
- **Purpose:** Generate narrative interpretation of prediction report
- **Inputs:** prediction report dict, domain str, verbosity level
- **Returns:** Full narrative text string
- **Called by:** `main.py:main()` when --ai flag set

### VedicInterpreter.__init__(api_key, model)
- **Purpose:** Initialize with OpenAI client; default model = GPT-4o

## IMPORTANT CONSTANTS
- `_AI_MODULE_AVAILABLE` flag in main.py controls whether this module is imported

## DEPENDENCIES
openai (optional — guarded import), prediction report dict format

## RECENT CHANGES
- 2026-03-02: Created as optional module
