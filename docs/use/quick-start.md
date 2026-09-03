---
icon: "material/rocket-launch"
---

# Quick Start Guide

## Output
The answer sets of flingo programs contain terms `val(x,v)`, where `x` is an integer variable occurring in the program and `v` is the integer value of the variable in the answer set. The absence of such a term means the variable is undefined.


## Language Reference

*flingo* atoms have the following forms, explore the links below for details on each construct

!!! tip

    Check out the [language reference](../language/index.md) for insight on how to show and hide variable assignments, as well as how to use choice rules in the head of a rule.

- [Sum under clingo semantics][sum-clingo]

Sums up all linear terms in the set. It can be seen as a generalization of clingo sum aggregates as it similarly removes undefined elements, and therefore always returns a value. It can be used in the head and in the body.

```clingo
&sum{lt1 : c1;...;ltn : cn} <> l0
```

- [Sum under strict semantics][sum-strict]

Sums up all linear terms in the set under strict semantics. Unlike the clingo sum aggregate, it does not remove undefined elements, and therefore may be undefined if any element is undefined. It can be used in the head and in the body.

```clingo
&sus{lt1 : c1;...;ltn : cn} <> l0
```

- [Assignments][assignments]

Is a directional assignment of a value between linear terms `lb` and `ub` to the variable `x`. It may only be used in the head of a rule. Only if `lb` and `ub` are defined, `x` will receive a value in between `lb` and `ub`. Note that this is different from using equality to assign a value.

```clingo
&in{lb..ub} =: x
```

- [Defined][defined]

May be used in the body to reason about whether a given variable `x` is defined or not. This is useful for instance to provide defaults or detect errors if a certain integer variable does not have a value but should.

```clingo
&df{x}
```

- [Minimum and maximum aggregates][min-max]

Sums up all linear terms in the set and returns the minimum or maximum value, respectively. It can be used in the head and in the body.

```clingo
&min{lt1 : c1;...;ltn : cn} <> l0
&max{lt1 : c1;...;ltn : cn} <> l0
```

!!! note

    - `lti`, `lb`, and `ub` are linear terms.
    - `ci` is a conjunction of literals for `i` between 0 and `n`.
    - `x` is the name of a variable.
    - `<>` is one of `<=`, `=`, `!=`, `<`, `>`, or `>=`.

