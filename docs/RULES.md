# Evaluation Semantics

Controls are evaluated against assets using a JsonLogic subset. The following
operators are supported:

- `==`, `!=`, `>`, `>=`, `<`, `<=`
- `in`, `and`, `or`, `!`

Helpers:

- `exists(var)` – true when the variable path exists
- `regex(var, pattern)` – matches a variable to a regular expression
- `contains(array, value)` – membership test

Assets are selected based on each control's `applies_to.types`. Missing fields
in an asset yield an `NA` result. When an exception selector matches a
control/asset pair the result status becomes `WAIVED` and the previous status is
stored in `meta.prev_status`.
