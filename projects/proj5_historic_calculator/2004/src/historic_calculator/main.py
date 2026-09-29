# A tiny "vector calculator" built on top of Numeric (the direct
# ancestor of NumPy). Provides a small command-line interface that
# applies a reduction such as `max`, `min`, `mean`, or `sum` to a
# comma-separated vector of numbers.
#
# Python 2.3 / 2.4 syntax notes:
#   - `print` is a statement, not a function
#   - no f-strings, no string.format(); use the `%` operator
import sys

import Numeric


USAGE = (
    "usage: hist_calc COMMAND VECTOR\n"
    "\n"
    "  COMMAND   one of: max, min, mean, sum\n"
    "  VECTOR    comma-separated numbers, e.g. 1,-2,4\n"
    "\n"
    "example:  hist_calc max 1,-2,4\n"
)


def make_vector(values):
    return Numeric.array(values, Numeric.Float)


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
    return Numeric.maximum.reduce(v)


def op_min(v):
    return Numeric.minimum.reduce(v)


def op_sum(v):
    return Numeric.sum(v)


def op_mean(v):
    return Numeric.sum(v) / len(v)


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


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(USAGE)
        return 2
    command = argv[1]
    vector_text = argv[2]
    try:
        result = run_calculator(command, vector_text)
    except ValueError, err:
        sys.stderr.write("error: %s\n" % err)
        sys.stderr.write(USAGE)
        return 1
    print "%s(%s) = %s" % (command, vector_text, result)
    return 0


def main_cli():
    # Zero-arg wrapper used as the setuptools `console_scripts` target.
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
