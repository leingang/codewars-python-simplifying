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

## Notes

I implemented this like the calculator katas, adding a `VARIABLE` token to the lexer,
and `Variable` and `ScalarMult` nodes to the AST.  Then variable counting was a matter
of visiting every node on the tree.  

My solution involved 12 classes and 328 lines of code.  It wasn't the shortest solution.

Here's a pretty concise solution I liked [link](https://www.codewars.com/kata/reviews/57f2cda6fbe78a9fed00011e/groups/5c1142a37bb2545ced0001a6).
It uses a single regex as tokenizer and parser.

    import re

    token = re.compile(r'([+-]?)\s*(\d*)\s*([a-zA-Z\(\)])')

    def substitute(formula, substitutes):
        res = formula
        for var, sub in substitutes:
            res = res.replace(var, '({})'.format(sub))
        return res if res == formula else substitute(res, substitutes)

    def reduce(tokens):
        res = dict()
        for sign, num, var in tokens:
            if var == ')':
                return res
            coef = int(sign + (num or '1'))
            if var == '(':
                for k, v in reduce(tokens).items():
                    res[k] = res.get(k, 0) + coef * v
            else:
                res[var] = res.get(var, 0) + coef
        return res

    def simplify(examples, formula):
        substitutes = [(k.strip(), v) for v, k in map(lambda x: x.split('='), examples)]
        subbed = substitute(formula, substitutes)
        reduced = reduce(iter(token.findall(subbed)))
        return ''.join(map('{0[1]}{0[0]}'.format, reduced.items()))

That `reduce` function is pretty interesting.  Haven't quite wrapped my head around it.
