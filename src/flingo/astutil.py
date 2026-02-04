"""
Tools to work with ASTs.
"""

import clingo


def match(term, name, arity):
    """
    Match the given term if it is a function with signature `name/arity`.
    """
    return (
        term.type
        in (
            clingo.TheoryTermType.Function,
            clingo.TheoryTermType.Symbol,
            clingo.Function,
            clingo.Symbol,
        )
        and term.name == name
        and len(term.arguments) == arity
    )
