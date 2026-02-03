import os

import nox

nox.options.sessions = "lint_flake8", "lint_pylint", "test"

PYTHON_VERSIONS = ["3.9"] if "GITHUB_ACTIONS" in os.environ else None


@nox.session
def format(session):
    session.install("-e", ".[format]")
    check = "check" in session.posargs

    autoflake_args = [
        "--in-place",
        "--imports=fillname",
        "--ignore-init-module-imports",
        "--remove-unused-variables",
        "-r",
        "flingo",
        "tests",
    ]
    if check:
        autoflake_args.remove("--in-place")
    session.run("autoflake", *autoflake_args)

    isort_args = ["--profile", "black", "flingo", "tests"]
    if check:
        isort_args.insert(0, "--check")
        isort_args.insert(1, "--diff")
    session.run("isort", *isort_args)

    black_args = ["flingo", "tests"]
    if check:
        black_args.insert(0, "--check")
        black_args.insert(1, "--diff")
    session.run("black", *black_args)


@nox.session
def lint_flake8(session):
    session.install("flake8", "flake8-black", "flake8-isort")
    session.run("flake8", "flingo")


@nox.session
def lint_pylint(session):
    session.install("-e", ".", "pylint")
    session.run("pylint", "flingo")


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    session.install("-e", ".")
    session.run("python", "-m", "unittest", "discover", "-v")
