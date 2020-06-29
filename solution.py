#!/usr/bin/env python

from collections import Counter, defaultdict
from operator import add, sub
import logging
import re

from utils import get_logger, add_logger
logger = get_logger(__name__)

logger.setLevel(logging.DEBUG)


class Token(object):
    """A token"""
    name = None
    value = None

    def __init__(self,name,value):

        self.name = name
        self.value = value

    def __str__(self):
        return "{cls}({name},{value})".format(cls=self.__class__.__name__,
                                            name=self.name,
                                            value=repr(self.value))
                                        

class TokenizerException(Exception): pass


class Lexer(object):
    """A lexical analyzer"""
    
    rules = None

    def __init__(self,rules):
        """Constructor

        *specs* is a list of tuples `(name,re)` or `(name,re,method)`
        where *name* is the token type, *re* is a regular expression
        matching the token, and *method* (optional) is the name of a
        lexer method to handle the token.

        E.g., `'skip'` will skip the token.
        """
        self.rules = rules

    def tokenize(self,text):
        """Tokenize *text*.  Yields a sequence of :class:`Token`s."""
        logger.debug("rules: {}".format(self.rules))
        token_re = "|".join('(?P<%s>%s)' % (rule[0],rule[1]) for rule in self.rules)
        handlers = defaultdict(str)
        for r in self.rules:
            if len(r)>2:
                handlers[r[0]] = r[2]
        # See https://stackoverflow.com/a/2359619/297797
        # and https://docs.python.org/3.2/library/re.html#writing-a-tokenizer
        pos = 0
        while True:
            m = re.compile(token_re).match(text,pos)
            if not m: break
            pos = m.end()
            tokname = m.lastgroup
            tokvalue = m.group(tokname)
            if handlers[tokname] == 'skip':
                pass 
            else:
                yield Token(tokname, tokvalue)
        if pos != len(text):
            raise TokenizerException('Tokenizer stopped at pos {pos}/{len} in {text}'\
                    .format(text=text,len=len(text),pos=pos))
        else:
            yield Token('EOF',None)


# Parsing
# =======

# The abstract syntax tree
# ------------------------

class AbstractSyntaxTree(object): 
    """Base type of an AST node"""
    
    def __str__(self):
        """String representation (mainly for introspection)"""
        return self.__class__.__name__


class Number(AbstractSyntaxTree):
    """AST node for a number."""

    def __init__(self,token):
        self.token = token
        self.value = int(token.value)

    def __str__(self):
        return "{}({})".format(self.__class__.__name__,self.value)


class Variable(AbstractSyntaxTree):
    """AST node for a variable."""

    def __init__(self,token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return "{}('{}')".format(self.__class__.__name__,self.value)



class BinOp(AbstractSyntaxTree):
    """AST node for a binary operator"""

    def __init__(self,left,op,right):
        self.left = left
        self.token = self.op = op
        self.right = right
    
    def __str__(self):
        return "{cls}({name},left={left},right={right})"\
            .format(cls=self.__class__.__name__,
                name=self.op.name,
                left=self.left,
                right=self.right)


class ScalarMult(AbstractSyntaxTree):
    """AST node for scalar multiplication"""

    def __init__(self,left,right):
        # only indicated in this grammar by juxtaposition, so no op token.
        self.left = left
        self.right = right

    def __str__(self):
        return "{cls}(left={left},right={right})"\
            .format(cls=self.__class__.__name__,
                left=self.left,
                right=self.right)


class UnaryOp(AbstractSyntaxTree):
    """AST node for a unary operator"""

    def __init__(self,op,expr):
        self.token = self.op = op
        self.expr = expr

    def __str__(self):
        return "{cls}({name},expr={expr})"\
            .format(cls=self.__class__.__name__,
                name=self.op.name,
                expr=self.expr)



# The parser object
# -----------------
class Parser(object):
    """Processor of a calculator token list to an abstract syntax tree"""

    lexer = None
    current_token = None
    tokens = None

    def __init__(self):
        self.lexer = Lexer([
            ('INTEGER',   r'[0-9]+'),
            ('PLUS',      r'\+'),
            ('MINUS',     r'-'),
            ('WHITESPACE',r'\s+', 'skip'),
            ('LPAREN',    r'\('),
            ('RPAREN',    r'\)'),
            ('IDENTIFIER', r'[a-zA-Z]')
        ])

    def parse(self,text):
        self.tokens = self.lexer.tokenize(text)
        self.current_token = next(self.tokens)
        return self.parse_expr()

    @add_logger
    def eat(self,token_type):
        """Eat a :class:`Token` of type *token_type*.

        Raise an error if the current token is not of type *token_type*.
        """
        if self.current_token.name == token_type:
            logger.debug("eating {}".format(token_type))
            self.current_token = next(self.tokens)
            logger.debug("self.current_token: {}".format(self.current_token))
        else:
            raise SyntaxError("Expected token of type '{}' but found '{}'"\
                                .format(token_type,self.current_token.name))

    @add_logger
    def parse_expr(self):
        """Parse an expression.

        Rules:

            expr: term (addop term)*
            addop: PLUS|MINUS
            term: MINUS term 
                  | INTEGER term
                  | VARIABLE
                  | LPAREN expr RPAREN

        Returns: :class:`AbstractSyntaxTree`
        """
        node = self.parse_term()
        while (self.match_addop()):
            node = self.parse_binop(left=node,right_callback=self.parse_term)
        return node

    @add_logger
    def parse_term(self):
        """Parse a term."""
        token = self.current_token
        if token.name == 'INTEGER':
            self.eat(token.name)
            node = self.parse_smult(left=Number(token),right_callback=self.parse_term)
        elif token.name == 'MINUS':
            self.eat(token.name)
            node = UnaryOp(token,self.parse_term())
        elif token.name == 'IDENTIFIER':
            self.eat(token.name)
            node = Variable(token)
        elif token.name == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expr()
            self.eat('RPAREN')
        else:
            raise SyntaxError("Unexpected token: {}".format(token))
        return node

    @add_logger
    def match_addop(self):
        """Check if the token matches an addop"""
        return self.current_token.name in ('PLUS','MINUS')

    @add_logger
    def parse_binop(self,left=None,right_callback=None):
        """Parse a binary operator."""
        op = self.current_token
        self.eat(self.current_token.name)
        if right_callback is None:
            right_callback = lambda : None
        node = BinOp(op=op,left=left,right=right_callback())
        return node


    @add_logger
    def parse_smult(self,left=None,right_callback=None):
        """Parse a scalar multiplication."""
        if right_callback is None:
            right_callback = lambda : None
        node = ScalarMult(left=left,right=right_callback())
        return node


class NodeVistor(object):
    """Visitor that recurses down a tree."""

    def visit(self,node):
        """Visit *node*.
        
        For each node class *cls* in the tree, looks for a method 
        :code:`visit_*cls*`.  If the method does not exist, calls
        :code:`generic_visit`.
        """
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self,method_name,'generic_visit')
        return visitor(node)

    def generic_visit(node):
        raise NotImplementedError


class Collector(NodeVistor):
    """Evaluator of an AST."""

    def __init__(self,parser=None):
        if parser is None:
            self.parser = Parser()
    
    @add_logger
    def visit_BinOp(self,node):
        operators = {
            'PLUS' : add,
            'MINUS' : sub
        }
        f = operators[node.op.name]
        counter_left, counter_right = self.visit(node.left),self.visit(node.right)
        logger.debug('f,left,right: {}({},{})'.format(f,counter_left,counter_right))
        result = Counter({
            k:(f(counter_left[k],counter_right[k]))
            for k in counter_left.keys() | counter_right.keys()
        })
        return result

    @add_logger
    def visit_Number(self,node):
        result = node.value
        return result

    @add_logger
    def visit_Variable(self,node):
        result = Counter()
        result[node.value] = 1
        return result

    @add_logger
    def visit_ScalarMult(self,node):
        scalar, counter = self.visit(node.left), self.visit(node.right)
        result = Counter({ k:(scalar * counter[k]) for k in counter})
        return result

    @add_logger
    def visit_UnaryOp(self,node):
        counter = self.visit(node.expr)
        result = Counter({ k:(-counter[k]) for k in counter})
        return result

@add_logger
def simplify(substitutions,expr):
    """Simplify the expression *expr* by using the substitution rules
    give in *substitutions.*
    """
    subst_expr = {}
    for rule in substitutions:
        subexpr, var = re.split(r'\s+=\s+',rule)
        subst_expr[var] = subexpr
    logger.debug('subst_expr: ' + str(subst_expr))
    # Repeat substitutions until there is only one variable left in the
    # expression
    while True:
        for var in subst_expr:
            expr = expr.replace(var,'(' + subst_expr[var] + ')')
            logger.debug('expr: ' + expr)
        var_counter = Counter(re.findall('[a-zA-Z]',expr))
        if len(var_counter) <= 1:
            break
    parser = Parser()
    expr_tree = parser.parse(expr)
    logger.debug('expr_tree: {}'.format(expr_tree))
    counter = Collector()
    ctr = counter.visit(expr_tree)
    logger.debug('ctr: {}'.format(ctr))
    result = ' + '.join('{}{}'.format(ctr[k],k) for k in ctr)
    return result
