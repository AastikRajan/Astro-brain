# Module: gpt_reasoner.py
## Last Updated: 2026-03-02

## PURPOSE
Implements GPT-4o chain-of-thought reasoning for complex astrological synthesis. Used by agent_swarm.py when deep reasoning is needed for multi-factor conflict resolution or when the engine's quantitative output needs expert-level interpretation. Separate from interpreter.py — focused on structured reasoning, not narrative.

## KEY FUNCTIONS

### reason_about_chart(chart_summary, question, context) → dict
- **Purpose:** Run structured GPT reasoning about a chart and question
- **Inputs:** chart summary str, question str, additional context dict
- **Returns:** `{reasoning_chain, conclusion, confidence, caveats}`
- **Called by:** `agent_swarm.py`

## DEPENDENCIES
openai (optional)

## RECENT CHANGES
- 2026-03-02: No changes
