# Module: significations.py
## Last Updated: 2026-03-02

## PURPOSE
Builds the planet-to-domain signification mapping used in confidence scoring. Maps each planet to the life domains it naturally signifies (career, finance, marriage, health, etc.) based on natural karakatwa and house significations. This map is what score_dasha_alignment() uses to check domain relevance.

## KEY FUNCTIONS

### get_planet_domain_map(planet_houses, house_lords, ...) → Dict[str, List[str]]
- **Purpose:** Build dynamic domain map for a specific chart
- **Inputs:** planet house placements, house lords, KP significations
- **Returns:** dict planet → list of domain strings it signifies
- **Called by:** `engine.py:analyze_static()`
- **Key logic:**
  - Natural karaka domains hard-coded (SUN→career/health, VENUS→marriage, etc.)
  - Added if planet lords or occupies domain house
  - KP significations add further domain links

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No changes
