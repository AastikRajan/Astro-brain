# Module: agent_swarm.py
## Last Updated: 2026-03-02

## PURPOSE
Orchestrates a multi-agent system for complex astrological queries that require specialized sub-analysis. Routes different aspects of a prediction query to specialized agents (dasha agent, transit agent, yoga agent, medical agent) and synthesizes their outputs into a unified response using GPT-4o coordination.

## KEY FUNCTIONS

### run_agent_swarm(chart_data, query, domain, specializations) → dict
- **Purpose:** Coordinate multiple specialized agents for a complex query
- **Inputs:** chart data dict, natural language query, domain, list of specializations
- **Returns:** `{agent_outputs, synthesized_answer, confidence, sources}`
- **Called by:** `main.py` in agent mode (--swarm flag)

## DEPENDENCIES
gpt_reasoner.py, engine.py, openai (optional)

## RECENT CHANGES
- 2026-03-02: No changes (scaffold module)
