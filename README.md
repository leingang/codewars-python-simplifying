# codewars-python-simplifying
A codewars python kata for simplifying algebraic expressions

## Description

You are given a list/array of example equalities such as:

    [ "a + a = b", "b - d = c ", "a + b = d" ]

Use this information to solve a given formula in terms of the remaining symbol such as:

    formula = "c + a + b"

in this example:

    "c + a + b" = "2a"

So the output is `"2a"`

### Notes:

* Variables names are case sensitive
* There might be whitespaces between the different characters. Or not...
* There should be support for parenthesis and their coefficient. Example: a + 3
  (6b - c).
* You might encounter several imbricated levels of parenthesis but you'll never
  get a variable as coefficient for parenthesis, only constant terms.
* All equations will be linear
* See the sample tests for clarification of what exactly the input/ouput
  formatting should be.

Without giving away too many hints, the idea is to substitute the examples into
the formula and reduce the resulting equation to one unique term. Look carefully
at the example tests: you'll have to identify the pattern used to replace
variables in the formula/other equations. Only one solution is possible for each
test, using this pattern, so if you keep asking yourself "but what if I do that
instead of...", that is you missed the thing.

## Developing

Use a python 3.6 virtual environment  I use the same one for all codewars katas:

    virtualenv-3.6 ~/.local/share/virtualenvs/codewars
    . ~/.local/share/virtualenvs/codewars/bin/activate

Then:

    python -m pip install -r requirements.txt

So far this only installs one python package: the Codewars test suite.

## Testing

Work in a module called `solution.py`.  Put the sample tests in `tests.py`.

The module `utils.py` provides a logging object whch is useful for debugging
and introspection.

## Submitting

Strip out the logging lines:

    sed -e '/logger/d' -e '/logging/d' solution.py | pbcopy

Then paste into the Codewars edit window.


