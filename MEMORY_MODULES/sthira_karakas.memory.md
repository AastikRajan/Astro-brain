# Module: sthira_karakas.py
## Last Updated: 2026-03-02

## PURPOSE
Provides the Sthira (fixed/permanent) Karaka assignments for different life significations. Unlike Chara Karakas (which vary by chart), Sthira Karakas are fixed for every chart: Sun always signifies father, Moon always signifies mother, Venus always signifies wife/husband, Jupiter always signifies children, etc.

## KEY FUNCTIONS

### get_sthira_karaka(domain) → str
- **Purpose:** Return the Sthira Karaka planet for a given life domain
- **Inputs:** domain string ("father", "mother", "spouse", "children", etc.)
- **Returns:** planet name string

## IMPORTANT CONSTANTS
Sthira Karaka table: father=SUN, mother=MOON/VENUS, spouse=VENUS(f)/JUPITER(m), children=JUPITER, elder_sibling=JUPITER, younger_sibling=MARS, spouse_elder=RAHU, spouse_younger=KETU, servants=SATURN, grandparents=RAHU/KETU

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No changes
