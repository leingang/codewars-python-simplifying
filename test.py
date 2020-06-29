#!/usr/bin/env python

import codewars_test as test
from solution import simplify


examples=[["a + a = b", "b - d = c", "a + b = d"],
          ["a + 3g = k", "-70a = g"],
          ["-j -j -j + j = b"],
          ["(-3f + q) + r = l","4f + q = r","-10f = q"],
          ["-(-(-(-(-(g))))) - l  = h","8l = g"],
          ["x = b","b = c","c = d","d = e"],
          ["y + 6Y - k - 6 K = f"," F + k + Y - y = K","Y = k","y = Y","y + Y = F"]
         ]
formula=["c + a + b",
         "-k + a",
         "-j - b",
         "20l + 20(q - 200f)",
         "h - l - g",
         "c",
         "k - f + y"
        ]
answer=["2a",
        "210a",
        "1j",
        "-4580f",
        "-18l",
        "1x",
        "14y"
       ]

for i in range(len(answer)):
    print('examples:' + str(examples[i]))
    print('formula:' + str(formula[i]))
    print('expected answer:'+str(answer[i]))
    test.assert_equals(simplify(examples[i],formula[i]),answer[i])






import re
from collections import Counter
from random import randrange as rand


def randomTests():
    
    class MyCounter(Counter):
        def __add__(self, other):  return MyCounter({ k: self[k] + other[k] for k in set(self.keys()) | set(other.keys()) })
        def __mul__(self, n):      return MyCounter({ k: self[k] * n        for k in self })
        __iadd__ = __add__
        __rmul__ = __imul__ = __mul__
        
    TOKENIZER = re.compile(r'[+-]?\d*[a-zA-Z]+|[+-]?\d*\(|\)')
    PARSE     = re.compile(r'([+-])?(\d*)?([a-zA-Z]+|[()])')
    
    def getMyCounter(part):
        def parser():
            mc = MyCounter()
            for tok in tokens:
                s,num,what = PARSE.findall(tok)[0]
                if   what == "(":  mc += int(s+(num or '1')) * parser()
                elif what == ")":  break
                else:              mc[what] += int(s+(num or '1'))
            return mc
        
        tokens = iter(TOKENIZER.findall(part.replace(" ","")))
        return parser()
    
    def simplifyInternal(examples,formula):
        space      = { right.strip(): getMyCounter(left) for eq in examples for left,right in [eq.split("=")] }
        toSimplify = getMyCounter(formula)
        
        while set(toSimplify.keys()) & set(space.keys()):
            for var in space:
                if var in toSimplify:
                    coef = toSimplify.pop(var)
                    toSimplify += space[var] * coef
                    
        return "{1}{0}".format(*toSimplify.popitem())
    
    
    
    """ ****************
          RANDOM TESTS
        ****************
    """
    
    DEBUG_RAND = False
    
    MIN_VARS   = 4
    ADD_VARS   = 3
    LOW_COEF   = -10
    RNG_COEF   = 30
    ZERO_PROBA     = 15
    BRACKETS_PROBA = 30
    DECREASE_PROBA = 12
    
    
    def getRandomSystem():
        
        def getVarPart(lvl, n):                                                # lvl: level of imbricated parenthesis / n: current variable name used / isFirst
            while True:
                coef = LOW_COEF//3 + rand(RNG_COEF//3)
                if not lvl or coef: break                                      # zero coefficient is not allowed at other levels than the first one
            
            if not coef: return ""                                             # may return blank only at first level
            
            varPart = "{}".format( lstVars[n] if rand(100) >= BRACKETS_PROBA - DECREASE_PROBA * lvl else
                                   "({})".format( " + ".join( getVarPart(lvl+1, rand(1,nVars)) for _ in range(rand(2,4)) ).replace("+ -", "- ") ))
            return "{}{}".format(coef, varPart)
        
        
        
        nVars = MIN_VARS + rand(ADD_VARS+1)                                    # number of variables names (all different)
        
        varSet = set()
        while len(varSet) < nVars:
            varSet.add( chr( [65,97][rand(2)] + rand(26) ))                    # generate names (1 letter only, lower and uppercase)
        
        lstVars = list(varSet)
        
        
        """ Generate the coefficients for all the variables in the examples:
              - First line left blank (will be the formula)
              - diagonal terms always 0: never find the current variable in its own definition
              - generate a triangular matrix, so that there are good odds that one can find a solution to the simplification
              - first variable will NEVER have a 0 coefficient
        """
        coefM = [ [ 0 if x == 0 or y >= x else                                   # first line blank ; upper triangle blank
                   (1 + rand(RNG_COEF//2)) * (-1)**rand(2) if y == 0 else        # first column: always != 0, positive or negative
                   (LOW_COEF + rand(RNG_COEF)) * (rand(100) >= ZERO_PROBA)       # other: any number in [LOW_COEF, LOW_COEF + RNG_COEF] or 0 with a probability of ZERO_PROBA
                      for y in range(nVars) ]
                 for x in range(nVars) ]
        
        def genEq(x):
            eq = " + ".join( "{}{}".format(coefM[x][y], lstVars[y]) for y in range(nVars) if coefM[x][y] ).replace("+ -", "- ") + " = " + lstVars[x]
            return re.sub(r'\b1(?=\w)', '', eq)
            
        """ Convert to examples equations """
        eqSyst = [ [""] if x == 0 else genEq(x) for x in range(nVars) ]
        
        
        """Generate the formula: does not contain the first variable """
        formula,x = '',0
        while not formula:
            x+=1
            if x==100:
                print("problem in the random tests: cannot generate a valid formula. Please raise an issue in the discourse with the info below:")
                print('vars:', lstVars,'nVars=',nVars,'\n')
                print('coefM:')
                print('\n'.join(map(str,coefM)))
                print('système:')
                print(eqSyst)
                raise Exception('nope')
                
            formula = " + ".join( part for part in [ getVarPart(0, n) for n in range(1, nVars) ]
                                       if part ).replace("+ -", "- ")
        eqSyst[0] = formula
            
        if DEBUG_RAND:
            print("------------")
            print( '\n'.join(str(eq) for eq in eqSyst))
        
        return eqSyst
    

    for _ in range(200):
        
        expected, formula = "INVALID", ""
        while expected == "INVALID":
            eqSyst   = getRandomSystem()
            examples = eqSyst[1:]
            formula  = eqSyst[0]
            expected = simplifyInternal(examples, formula)
            
            if DEBUG_RAND and expected == "INVALID":  print("********\n" + expected + "\n********")
        
        if True:  print("---------\nExamples:\t{}\nFormula:\t{}\nExpected:\t{}".format(examples, formula, expected))
        
        test.assert_equals(simplify(examples, formula), expected)

randomTests()
    