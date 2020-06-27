# codewars-python-simplifying
A codewars python kata for simplifying algebraic expressions

## Description

You are given a list/array of example equalities such as:

    [ "a + a = b", "b - d = c ", "a + b = d" ]
Use this information to solve a given formula in terms of the remaining symbol such as:

    formula = "c + a + b"

in this example:

    "c + a + b" = "2a"

So the output is "2a"

### Notes:

* Variables names are case sensitive
* There might be whitespaces between the different characters. Or not...
* There should be support for parenthesis and their coefficient. Example: a + 3 (6b - c).
* You might encounter several imbricated levels of parenthesis but you'll never get a variable as coefficient for parenthesis, only constant terms.
* All equations will be linear
* See the sample tests for clarification of what exactly the input/ouput formatting should be.

Without giving away too many hints, the idea is to substitute the examples into the formula and reduce the resulting equation to one unique term. Look carefully at the example tests: you'll have to identify the pattern used to replace variables in the formula/other equations. Only one solution is possible for each test, using this pattern, so if you keep asking yourself "but what if I do that instead of...", that is you missed the thing.
