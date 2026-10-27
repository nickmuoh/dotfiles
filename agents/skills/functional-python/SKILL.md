---
name: functional-python
description: Use when implementing or refactoring Python data management, transformations, or orchestration where functional design could simplify the code.
---

# Functional Python

Use functional programming principles to make Python data and behavior easier to understand. Apply them when they simplify the code; keep the solution idiomatic and fit for its domain. This guidance is based on [Functionally Zen](https://testdouble.com/insights/functionally-zen).

## Choose the shape that clarifies intent

- Keep domain data explicit. When callers can see and provide the data, represent it with ordinary Python values or a simple data object, and compose functions that transform or inspect it. This makes the relationship between the data and each operation visible.
- Prefer a function to a method when the operation does not depend on hidden object state. Prefer small functions with clear inputs and outputs over functions or classes that bury rules in implicit state.
- Use a class when it owns meaningful internal state, protects invariants, or has a lifecycle that belongs to the object. Keep that state encapsulated; expose operations that express what the object does.
- Represent stable rules and lookup tables as data when that is clearer than encoding them in branching logic.
- Keep calculations and decisions pure where practical. Keep file, database, network, and user-interface effects at clear boundaries, then pass their results into the data transformations.
- Keep constructors predictable: pass in ready-to-use values rather than performing external work during construction.
- Follow familiar Python idioms. Use a comprehension for a simple transformation when it reads more clearly than `map()` or `filter()`. Prefer ordinary mutable structures when mutation is the clearest fit.
- Prefer tests of pure behavior without mocks. Test effectful boundaries with integration tests or mocks when isolation helps; mock-heavy tests can signal tangled dependencies, but are not automatically wrong.

Apply this as a design hint, not a conversion rule. Use the functional shape when it reduces hidden state, indirection, or test setup. Keep the existing object-oriented shape when it expresses ownership or lifecycle more clearly. Preserve public behavior and local conventions.
