# PyJHora Gap Analysis — STRUCTURE SCAN ONLY
# DO NOT read file contents. Only scan structure and function names.
# Budget: minimal tokens. Output: gap list only.

---

## STEP 1: Scan PyJHora folder structure (2 levels deep only)

```
dir /s /b "C:\Users\aasti\Downloads\New folder (3)\refrence\PyJHora-main\src\jhora" | findstr /i ".py$"
```

This gives you every .py file path. List them grouped by folder.

## STEP 2: For each .py file, extract ONLY function names (not code)

Use this pattern for each file:
```python
import ast, os
for root, dirs, files in os.walk(r"C:\Users\aasti\Downloads\New folder (3)\refrence\PyJHora-main\src\jhora"):
    for f in files:
        if f.endswith('.py') and not f.startswith('__'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    tree = ast.parse(fh.read())
                funcs = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if funcs:
                    # Only print module path (relative) + function count + function names
                    rel = os.path.relpath(path, r"C:\Users\aasti\Downloads\New folder (3)\refrence\PyJHora-main\src")
                    print(f"\n{rel} ({len(funcs)} functions):")
                    for fn in funcs:
                        print(f"  {fn}")
            except:
                pass
```

Run this ONCE. Save output to `pyjhora_functions.txt`.

## STEP 3: Scan OUR function names the same way

```python
import ast, os
for root, dirs, files in os.walk(r"C:\Users\aasti\Downloads\New folder (3)\vedic_engine"):
    for f in files:
        if f.endswith('.py') and not f.startswith('__'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    tree = ast.parse(fh.read())
                funcs = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if funcs:
                    rel = os.path.relpath(path, r"C:\Users\aasti\Downloads\New folder (3)")
                    print(f"\n{rel} ({len(funcs)} functions):")
                    for fn in funcs:
                        print(f"  {fn}")
            except:
                pass
```

Run this ONCE. Save output to `our_functions.txt`.

## STEP 4: Compare and output gap analysis

Read both text files. For each PyJHora module/function, check if we have an equivalent.

Output `content44_pyjhora_gaps.txt` with this format:

```
PYJHORA GAP ANALYSIS
====================

SECTION 1: DASHA SYSTEMS THEY HAVE, WE DON'T
---------------------------------------------
- buddhi_gathi dasha: [brief — what is it from function name]
- kaala dasha: [brief]
... etc

SECTION 2: RASI DASHAS THEY HAVE, WE DON'T  
---------------------------------------------
- chakra dasha: [brief]
- kendradhi_rasi dasha: [brief]
... etc

SECTION 3: DATA FILES THEY HAVE
--------------------------------
List all files in their data/ folder (just filenames + sizes)

SECTION 4: COMPUTATION MODULES THEY HAVE, WE DON'T
----------------------------------------------------
Any module category we completely lack

SECTION 5: THINGS WE HAVE THAT THEY DON'T
-------------------------------------------
Our unique modules not in PyJHora

SECTION 6: THEIR TEST SUITE
-----------------------------
How many tests? What do they test? (just scan test file names + count)
```

## RULES
- DO NOT read any .py file contents beyond AST function name extraction
- DO NOT copy any code
- DO NOT implement anything
- ONLY produce the gap analysis text file
- Total output: content44_pyjhora_gaps.txt