#!/usr/bin/env python

import codewars_test as Test
from solution import simplify


examples=[["a + a = b", "b - d = c", "a + b = d"],
          ["a + 3g = k", "-70a = g"],
          ["-j -j -j + j = b"]
         ]
formula=["c + a + b",
         "-k + a",
         "-j - b"
        ]
answer=["2a",
        "210a",
        "1j"
       ]

for i in range(len(answer)):
    print('examples:' + str(examples[i]))
    print('formula:' + str(formula[i]))
    print('expected answer:'+str(answer[i]))
    
    Test.assert_equals(simplify(examples[i],formula[i]),answer[i])

