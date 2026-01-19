"""
This file intentionally contains no tests.

Reason:
--------
The only utility currently present in `VideoSharingApp.utils`
is a custom logger configuration wrapper around Python's
built-in `logging` module.

After evaluation, I chose NOT to unit-test the logger because:
- It contains no business logic
- It primarily delegates to the standard library
- Testing it would require filesystem and handler mocking with low confidence-to-effort ratio
- Logging correctness is validated via integration/runtime behavior

This file exists as an explicit architectural decision to:
- Document the choice
- Avoid reintroducing low-value tests in the future
- Keep test coverage focused on behavior, not infrastructure glue

If additional utility functions with business logic are added later,
this file should be revisited.
"""
