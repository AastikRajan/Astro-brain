# PROJECT RULEBOOK — Mandatory for All Code Changes

> Any agent or developer making changes to this codebase MUST follow these rules.
> Read `MEMORY_INDEX.md` first, then the relevant `MEMORY_MODULES/` file, THEN code.

---

## Rule 1: Memory Update Required

After ANY code change, you MUST update:
1. The relevant `MEMORY_MODULES/[file].memory.md` — update the function description, key logic, and add entry to RECENT CHANGES
2. `MEMORY_INDEX.md` Section B — update the "Last Modified" date for that file
3. `MEMORY_INDEX.md` Section D — if any constant/weight/threshold changed, update it
4. `CHANGELOG.md` — add a one-line entry (see Rule 2)

---

## Rule 2: Changelog Format

Every change gets ONE line in `CHANGELOG.md`:

```
[DATE] [FILE] [CHANGE TYPE] — [Short description]
```

Change types: `ADD`, `FIX`, `REMOVE`, `REFACTOR`, `WIRE`

Example:
```
2026-03-02 confidence.py ADD — Karaka-specific BAV mapping (DOMAIN_KARAKA_BAV_MAP)
2026-03-02 bayesian_layer.py FIX — Dasha↔transit overlap merge (was double-counting)
2026-03-02 confidence.py REMOVE — house_lord_strength zeroed out (double-counted with Promise gate)
```

---

## Rule 3: No Silent Side Effects

If changing one module affects another module's behavior, you MUST:
1. Document the cross-module impact in BOTH memory files
2. Note it in the changelog as `[FILE1] → affects [FILE2]`

Example:
```
2026-03-02 confidence.py REMOVE — W_HOUSE_LORD=0.00 → affects bayesian_layer.py prior weighting
```

---

## Rule 4: Test After Every Change

After any code change, run the test chart to verify:
1. Output still generates without errors (EXIT:0)
2. All sections present in output
3. Confidence values are within reasonable range (0.10–0.95)

Run with:
```bash
python main.py
```

---

## Rule 5: Constants Are Sacred

Never change a constant/weight/threshold without:
1. Documenting WHY in the changelog
2. Recording the OLD value and NEW value in the changelog entry
3. Updating `MEMORY_INDEX.md` Section D with the new value

Example changelog entry for constant change:
```
2026-03-02 confidence.py REFACTOR — W_DASHA: 0.30 → 0.25 (redistributed to transit+yoga after BAV karaka add)
```

---

## Rule 6: Read Memory Before Coding

Before making ANY change:
1. Read `MEMORY_INDEX.md` (understand the full system, data flow, constants)
2. Read the relevant `MEMORY_MODULES/[file].memory.md` (understand the specific module's functions, callers, dependencies)
3. THEN make the change

This saves tokens and prevents redundant code or conflicting logic.

---

## Rule 7: One Change at a Time

Do not bundle unrelated changes in a single edit session. Each logical change should be:
- A single coherent modification to one or two files
- Fully tested before proceeding to the next change
- Documented in CHANGELOG.md before closing the session

---

## Rule 8: Never Duplicate Logic

Before adding a new function, check:
1. `MEMORY_INDEX.md` Section B — does a similar function already exist?
2. `MEMORY_MODULES/` — does the target module already compute something similar?
3. `config.py` — is there already a constant for this value?

If yes: extend the existing function rather than creating a duplicate.
