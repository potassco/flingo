"""
Main module providing the application logic.
"""

import sys
import time

import clingo
from clingcon import ClingconTheory
from clingo.ast import Location, Position, ProgramBuilder, Rule, parse_files

from flingo import THEORY
from flingo.parsing import HeadBodyTransformer
from flingo.translator import AUX, Translator

MAX_INT = 1073741823
MIN_INT = -1073741823
CSP = "__csp"
DEF = "__def"
VAL = "__val"


class Statistic:
    """
    Class for statistics of flingo translation.
    """

    # NOTE: better use a dataclass instead
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.rewrite_ast = 0
        self.translate_program = 0
        self.atoms_added = 0
        self.rules_added = 0
        self.variables_added = 0


class AppConfig:
    """
    Class for application specific options.
    """

    # NOTE: better use a dataclass instead
    # pylint: disable=too-few-public-methods,too-many-positional-arguments

    def __init__(self, min_int, max_int, print_translation, print_auxiliary, defined):
        self.print_aux = print_auxiliary
        self.print_trans = print_translation
        self.min_int = min_int
        self.max_int = max_int
        self.defined = defined


class FlingoApp(clingo.Application):
    """
    Application class that can be used with `clingo.clingo_main` to solve AMT
    problems.
    """

    def __init__(self):
        self.program_name = "flingo"
        self.version = "v1.0.0"
        self.config = AppConfig(MIN_INT, MAX_INT, clingo.Flag(False), clingo.Flag(False), DEF)
        self.stats = Statistic()
        self._theory = ClingconTheory()
        self._answer = 0

    def __on_model(self, model):
        """
        Report models to the propagator.
        """
        self._theory.on_model(model)
        defined_variables = {
            atom.arguments[0]
            for atom in model.symbols(atoms=True)
            if atom.match(self.config.defined,1)
        }
        # print(model.symbols(shown=True,atoms=True))
        valuation_symbols = []
        for assignment in model.symbols(theory=True):
            if not assignment.match(CSP,2):
                continue
            variable, value = assignment.arguments
            if variable.name == AUX or variable not in defined_variables:
                continue
            valuation_symbols.append(clingo.Function(VAL, [variable, value]))
        model.extend(valuation_symbols)

    def print_model(self, model, printer):
        """
        Print the model in the desired format.
        """
        assert printer is not None
        shown = []
        # Shown symbols excluding _def
        shown += [str(symbol) for symbol in model.symbols(shown=True) if not symbol.match(self.config.defined, 1)]

        # Valuation symbols extracted for the extended ones in __on_model
        for symbol in sorted(model.symbols(theory=True)):
            if symbol.match(VAL, 2):
                name, value = symbol.arguments
                shown.append(f"val({name},{value})")

        # Auxiliary symbols
        if self.config.print_aux:
            shown += [
                str(atom)
                for atom in model.symbols(atoms=True)
                if atom.match(self.config.defined, 1)
            ]
            auxvars = [
                "val(" + str(assignment.arguments[0]) + "," + str(assignment.arguments[1]) + ")"
                for assignment in model.symbols(theory=True)
                if assignment.match(CSP, 2) and assignment.arguments[0].name == AUX
            ]
            shown.extend(auxvars)

        sys.stdout.write(" ".join(shown))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _flag_str(self, flag):
        return "yes" if flag else "no"

    def _parse_defined_predicate(self, name):
        if name[0].islower() and name.contains("[a-zA-Z0-9]+"):
            self.config.defined = name
            return True
        return False

    def register_options(self, options):
        """
        Register flingo related options.
        """

        self._theory.register_options(options)

        group = "Translation Options"
        options.add_flag(
            group,
            "print-auxvars,@2",
            f"Print value of auxiliary variables [{self._flag_str(self.config.print_aux)}]",
            self.config.print_aux,
        )
        options.add_flag(
            group,
            "print-translation,@2",
            f"Print translation [{self._flag_str(self.config.print_trans)}]",
            self.config.print_trans,
        )
        options.add(
            group,
            "defined-predicate",
            f"Name of the defined predicate [{self.config.defined}]",
            self._parse_defined_predicate,
        )

    def __on_statistics(self, step, akku):
        self._theory.on_statistics(step, akku)
        akku["flingo"] = {}
        flingo = akku["flingo"]
        flingo["Translation time in seconds"] = {}
        translation = flingo["Translation time in seconds"]
        translation["AST rewriting"] = self.stats.rewrite_ast
        translation["Translation"] = self.stats.translate_program
        flingo["Number of variables added"] = self.stats.variables_added
        flingo["Number of atoms added"] = self.stats.atoms_added
        flingo["Number of rules added"] = self.stats.rules_added
        return True

    def _read(self, path):
        if path == "-":
            return sys.stdin.read()
        with open(path, encoding="utf-8") as file_:
            return file_.read()

    def main(self, control, files):
        """
        Entry point of the application registering the propagator and
        implementing the standard ground and solve functionality.
        """
        self._theory.register(control)
        self._theory.configure("max-int", str(self.config.max_int))
        self._theory.configure("min-int", str(self.config.min_int))

        if not files:
            files = ["-"]

        start = time.time()
        with ProgramBuilder(control) as bld:
            hbt = HeadBodyTransformer()
            parse_files(
                files,
                lambda stm: bld.add(hbt.visit(stm)),
            )
            pos = Position("<string>", 1, 1)
            loc = Location(pos, pos)
            for rule in hbt.rules_to_add:
                bld.add(Rule(loc, rule[0], rule[1]))
        end = time.time()
        self.stats.rewrite_ast = end - start  # type: ignore

        control.add("base", [], THEORY)
        control.ground([("base", [])])

        start = time.time()
        translator = Translator(control, self.config, self.stats)
        translator.translate(control.theory_atoms)
        end = time.time()
        self.stats.translate_program = end - start  # type: ignore

        self._theory.prepare(control)
        control.solve(on_model=self.__on_model, on_statistics=self.__on_statistics)  # type: ignore


def main():
    """
    Main function executing the flingo application.
    """

    arguments = sys.argv[1:]
    sys.exit(int(clingo.clingo_main(FlingoApp(), arguments)))


if __name__ == "__main__":
    main()
