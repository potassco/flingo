"""
This module contains functions for parsing and normalizing constraints.
"""

import clingo
from clingo import ast

PREFIX = "__f"
HEAD = "_h"
BODY = "_b"
THEORY = (
    """\
#theory htc {
    function_term {};
    sum_term {
    -  : 3, unary;
    ** : 2, binary, right;
    *  : 1, binary, left;
    /  : 1, binary, left;
    \\ : 1, binary, left;
    +  : 0, binary, left;
    -  : 0, binary, left
    };
    dom_term {
    -  : 4, unary;
    ** : 3, binary, right;
    *  : 2, binary, left;
    /  : 2, binary, left;
    \\ : 2, binary, left;
    +  : 1, binary, left;
    -  : 1, binary, left;
    .. : 0, binary, left
    };
    &"""
    + PREFIX
    + """sum"""
    + BODY
    + """/0 : sum_term, {<=,=,!=,<,>,>=}, sum_term, body;
    &"""
    + PREFIX
    + """sum"""
    + HEAD
    + """/0 : sum_term, {<=,=,!=,<,>,>=,=:}, sum_term, head;
    &"""
    + PREFIX
    + """sus"""
    + BODY
    + """/0 : sum_term, {<=,=,!=,<,>,>=}, sum_term, body;
    &"""
    + PREFIX
    + """sus"""
    + HEAD
    + """/0 : sum_term, {<=,=,!=,<,>,>=,=:}, sum_term, head;
    &"""
    + PREFIX
    + """max"""
    + BODY
    + """/0 : sum_term, {<=,=,!=,<,>,>=}, sum_term, body;
    &"""
    + PREFIX
    + """max"""
    + HEAD
    + """/0 : sum_term, {<=,=,!=,<,>,>=,=:}, sum_term, head;
    &"""
    + PREFIX
    + """min"""
    + BODY
    + """/0 : sum_term, {<=,=,!=,<,>,>=}, sum_term, body;
    &"""
    + PREFIX
    + """min"""
    + HEAD
    + """/0 : sum_term, {<=,=,!=,<,>,>=,=:}, sum_term, head;
    &"""
    + PREFIX
    + """in"""
    + HEAD
    + """/0 : dom_term, {=:}, sum_term, head;
    &df/0 : function_term, body
}.
"""
)


class HeadBodyTransformer(ast.Transformer):
    """
    Class for tagging location of theory atoms.
    """

    # pylint: disable=invalid-name

    def __init__(self) -> None:
        self.rules_to_add = []

    def _rewrite_tuple(self, element, number):
        """
        Add variables to tuple to ensure multiset semantics.
        """

        element.terms = list(element.terms)
        if number is not None:
            element.terms.append(ast.SymbolicTerm(element.terms[0].location, clingo.Number(number)))

        return element

    def _rewrite_tuples(self, elements):
        """
        Add variables to tuples of elements to ensure multiset semantics.
        """
        elements = [new_element for element in elements for new_element in element.unpool()]
        if len(elements) == 1:
            return elements

        return [self._rewrite_tuple(element, n) for n, element in enumerate(elements)]

    def visit_Literal(self, lit, in_lit=False):
        """
        Visit all literals.
        """
        assert in_lit is not None
        return lit.update(**self.visit_children(lit, True))

    def visit_TheoryAtom(self, atom, in_lit=False):
        """
        Rewrite theory atoms depending on location.
        """
        term = atom.term
        if term.name in ["sum", "sus", "in", "max", "min"] and not term.arguments:
            loc = BODY if in_lit else HEAD
            atom = atom.update(
                term=ast.Function(
                    term.location,
                    PREFIX + term.name + loc,
                    [],
                    False,
                ),
                elements=self._rewrite_tuples(atom.elements),
            )
        return atom

    def visit_Rule(self, rule):
        """
        Rewrite rules.
        """
        head = rule.head
        location = head.location
        if head.ast_type == ast.ASTType.TheoryAtom:
            new_elements = []
            for element in head.elements:
                term = element.terms[0]
                condition = element.condition
                if term.ast_type == ast.ASTType.TheoryUnparsedTerm and "::" in str(term):
                    unparsed_terms = term.elements[:-1]
                    choice_atom = term.elements[-1].term
                    assert (
                        "::" == term.elements[-1].operators[0]
                        and choice_atom.ast_type in [ast.ASTType.TheoryFunction, ast.ASTType.SymbolicTerm]
                        and len(element.terms) == 1
                    )
                    if choice_atom.ast_type == ast.ASTType.TheoryFunction:
                        choice_atom = ast.Literal(
                            location,
                            0,
                            ast.SymbolicAtom(ast.Function(location, choice_atom.name, choice_atom.arguments, 0)),
                        )
                    else:
                        choice_atom = ast.Literal(location, 0, ast.SymbolicAtom(choice_atom))
                    choice = ast.Aggregate(
                        location,
                        None,
                        [ast.ConditionalLiteral(location, choice_atom, [])],
                        None,
                    )
                    body = []
                    body.extend(rule.body)
                    body.extend(condition)
                    self.rules_to_add.append((choice, body))
                    new_element_condition = [choice_atom]
                    new_element_condition.extend(condition)
                    new_elements.append(
                        ast.TheoryAtomElement(
                            [ast.TheoryUnparsedTerm(location, unparsed_terms)],
                            new_element_condition,
                        )
                    )
                else:
                    new_elements.append(element)
            rule.head.elements = new_elements
        return rule.update(**self.visit_children(rule))
