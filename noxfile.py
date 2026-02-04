import os

import nox

nox.options.sessions = "lint_ruff", "lint_pylint", "test"

PYTHON_VERSIONS = ["3.12"] if "GITHUB_ACTIONS" in os.environ else None


@nox.session
def lint_ruff(session):
    """
    Check code style using Ruff.
    """
    session.install("-e", ".[lint_ruff]")
    session.run("ruff", "check")
    session.run("ruff", "format", "--diff")


@nox.session
def lint_pylint(session):
    """
    Check code style using Pylint.
    """
    session.install("-e", ".[lint_pylint]")
    session.run("pylint", "src", "tests")


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    """
    Run the test suite with coverage.
    """
    session.install("-e", ".[test]")
    session.run("coverage", "run", "-m", "unittest", "discover", "-v")
    # NOTE: better aim for 100% coverage, but 87% is the current level.
    session.run("coverage", "report", "-m", "--fail-under=87")


@nox.session
def dev(session):
    """
    Install all development dependencies.
    """
    session.install("-e", ".[dev]")
