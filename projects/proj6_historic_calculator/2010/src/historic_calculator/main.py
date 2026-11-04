# A tiny "vector calculator" built on top of NumPy. Provides a small
# command-line interface that applies a reduction such as `max`, `min`,
# `mean`, or `sum` to a comma-separated vector of numbers.
#
# Python 2.7 syntax notes:
#   - `print` is still a statement (the function form is available via
#     `from __future__ import print_function` but we stick with the
#     idiomatic 2.x form here)
#   - `argparse` is part of the standard library by the 2.7 era, so we
#     can use it for a more typical 2014-style CLI.
import argparse
import sys

import numpy


def make_vector(values):
    return numpy.array(values, dtype=numpy.float64)


def parse_vector(text):
    parts = text.split(",")
    numbers = []
    for part in parts:
        part = part.strip()
        if part == "":
            raise ValueError("empty value in vector: %s" % text)
        numbers.append(float(part))
    if len(numbers) == 0:
        raise ValueError("vector must contain at least one number")
    return make_vector(numbers)


def op_max(v):
    return numpy.max(v)


def op_min(v):
    return numpy.min(v)


def op_sum(v):
    return numpy.sum(v)


def op_mean(v):
    return numpy.mean(v)


COMMANDS = {
    "max":  op_max,
    "min":  op_min,
    "sum":  op_sum,
    "mean": op_mean,
}


def run_calculator(command, vector_text):
    if command not in COMMANDS:
        raise ValueError("unknown command: %s" % command)
    vector = parse_vector(vector_text)
    return COMMANDS[command](vector)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Apply a reduction to a comma-separated vector.",
    )
    parser.add_argument(
        "command",
        choices=sorted(COMMANDS.keys()),
        help="operation to run",
    )
    parser.add_argument(
        "vector",
        help="comma-separated numbers, e.g. 1,-2,4",
    )
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        result = run_calculator(args.command, args.vector)
    except ValueError as err:
        parser.exit(1, "error: %s\n" % err)
        return 1
    print "%s(%s) = %s" % (args.command, args.vector, result)
    return 0


def main_cli():
    # Zero-arg wrapper used as the setuptools `console_scripts` target.
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
