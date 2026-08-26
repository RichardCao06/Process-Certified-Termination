# PCT P2 Natural-Pilot Preflight Input Request v0.1

The D13-D18 choices are approved and all unaffected reversible protocol work is complete. The pilot remains blocked by operational inputs rather than an unresolved choice among the approved A/B/C options.

## Required Worker profile manifest

Provide a sanitized record for the intended `DeepSeek V4-Pro` profile containing no key or secret:

```text
provider route
provider account/tenant scope identifier, if needed for reproducibility
returned exact model identifier
model revision or snapshot
profile/config SHA-256
system-prompt SHA-256
tool-catalog SHA-256
reasoning settings
sampling settings
retry policy
context-window limit
maximum output limit
per-trajectory token cap
per-trajectory monetary cap and currency
```

A display alias alone is insufficient. A substitute model is prohibited. If the exact intended profile cannot be identified, a smaller Worker-configuration Human Gate must be opened.

## Required Reference custody assignment

Assign two different independent blinded human raters for the 10 semi-open tasks and identify the adjudication role. The assignment may use pseudonymous study IDs; personal data is unnecessary. Neither rater may see the other judgment, Shadow verdict, or adjudication before submitting the independent pass.

Until both input groups are frozen and `scripts/validate_p2_natural_pilot_preflight.py` reports PASS, no natural-task Worker call or Reference opening is authorized.
