# Module: config.py
## Last Updated: 2026-03-02

## PURPOSE
Single source of truth for all constants, enumerations, and lookup tables in the Vedic astrology engine. All other modules import from here. Contains planet/sign enums, sign lords, nakshatra data, Shadbala minimums, transit tables, Gochar effects, Vedha pairs, Ashtakvarga contribution matrices, and all timing system year allocations.

## KEY FUNCTIONS
No functions — pure constants and dataclass definitions.

## IMPORTANT CONSTANTS
- `Planet` enum — 9 planets with IntEnum indices (SUN=0 through KETU=8)
- `Sign` enum — 12 signs with IntEnum indices (ARIES=0 through PISCES=11)
- `SIGN_LORDS` — sign index → planet name
- `NAKSHATRA_NAMES` — 27 nakshatra names
- `NAKSHATRA_SPAN = 13.333...°` per nakshatra
- `VIMSHOTTARI_YEARS` — planet → dasha years (SUN=6,MOON=10,...,KETU=7, total=120)
- `VIMSHOTTARI_SEQUENCE` — [KETU,VENUS,SUN,MOON,MARS,RAHU,JUPITER,SATURN,MERCURY]
- `ASHTOTTARI_YEARS` — 108-yr cycle allocations
- `SHADBALA_MINIMUMS` — required virupas per planet
- `EXALTATION_DEGREES`, `DEBILITATION_DEGREES` — peak/fall exact longitudes
- `OWN_SIGNS`, `MOOLATRIKONA` — planet → sign ownership dicts
- `NATURAL_BENEFICS = {MOON, MERCURY, JUPITER, VENUS}`
- `NATURAL_MALEFICS = {SUN, MARS, SATURN, RAHU, KETU}`
- `COMBUSTION_DEGREES` — orbs per planet for combustion check
- `GOCHAR_EFFECTS` — house-from-moon → score dict for transit Gochar
- `VEDHA_TABLE` — Vedha obstruction pairs per sign
- `VEDHA_EXCEPTIONS` — planets exempt from Vedha
- `VEDHA_REDUCTION = 0.5` — multiplier when Vedha applies
- `TRANSIT_FAVORABLE` — set of favorable Gochar placements
- `KAKSHYA_LORDS`, `KAKSHYA_SPAN` — KP Kakshya breakdown
- `MANIFESTATION_ZONES` — degree ranges for high-manifestation bonus
- `MANIFESTATION_OUTSIDE_MULTIPLIER` — multiplier outside zones
- `NAISARGIKA_FRIENDS`, `NAISARGIKA_ENEMIES` — natural friendship tables
- `SIGN_ELEMENTS` — sign → Element enum mapping
- `ELEMENT.FIRE/EARTH/AIR/WATER` — sign element categories

## DEPENDENCIES
(none — root module)

## RECENT CHANGES
- 2026-03-02: Added MANIFESTATION_ZONES and KAKSHYA_LORDS/KAKSHYA_SPAN constants
- 2026-03-02 Phase 1A FIX: SAPTAVARGAJA_SCORES corrected to classical Research File 1 values:
  EXALTED: 45→30 (bypass = OWN), GREAT_FRIEND: 22.5→20, NEUTRAL: 7.5→10,
  ENEMY: 3.75→4, GREAT_ENEMY: 1.875→2, DEBILITATED: 0→2 (bypass = GREAT_ENEMY)
