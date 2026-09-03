---
hide:
  - navigation
  - toc
---

# flingo

*flingo* is a solver for Answer Set Programming (ASP) combined with founded conditional linear constraints. These constraints enable the user to use integer variables that are not subject to grounding. Integer variables may be undefined and, in line with the philosophy of ASP, there needs to be a justification in the logic program if a variable receives a value in an answer set. Conditionality allows for a generalization of aggregates commonly used in ASP.


### Relation to clingo
*flingo* is an extension of [clingo](https://potassco.org/clingo) and accepts as input clingo rules enriched with founded conditional linear constraints.

### Relation to clingcon
*flingo* relies on the constraint answer set programming (CASP) solver [clingcon](https://potassco.org/clingcon) into whose language a *flingo* program is translated. *flingo*'s two main advantages are foundedness of the integer variables and aggregates over integer variables. The former allows variables to be undefined and only assume a value if a reason for that value can be derived. This differs to the behavior of CASP, where variables are always defined and in absence of any constraint to a variable, all possible values are enumerated. The latter generalizes ASP aggregates to contain integer variables that are not subject to grounding.

### Output
The answer sets of flingo programs contain terms `val(x,v)`, where `x` is an integer variable occurring in the program and `v` is the integer value of the variable in the answer set. The absence of such a term means the variable is undefined. Take a look into the [Language Reference](docs/reference/language/index.md) for details on the different constructs and examples.

!!! info
    *flingo* is part of the [Potassco](https://potassco.org) suite.


## Cite

!!! quote "Citation"

    **FLINGO -- Instilling ASP Expressiveness into Linear Integer Constraints**
    Jorge Fandinno, Pedro Cabalar, Philipp Wanko, Torsten Schaub
    [arXiv:2602.09620](https://arxiv.org/abs/2602.09620)

    ```bibtex
    @article{facawasc26a,
      title   = {FLINGO -- Instilling ASP Expressiveness into Linear Integer Constraints},
      author  = {J. Fandinno and P. Cabalar and P. Wanko and T. Schaub},
      journal = {arXiv preprint arXiv:2602.09620},
      year    = {2026},
      url     = {https://arxiv.org/abs/2602.09620}
    }
    ```
