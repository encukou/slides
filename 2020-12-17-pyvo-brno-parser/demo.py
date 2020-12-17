main_example = """
# Quadratic equation:  ax² + bx + c = 0

a = 1
b = -4
c = 2

discriminant = b*b - 4*a*c

if discriminant < 0: error!

x1 = (0-b + sqrt(STOP_HERE)) / 2
x2 = (0-b - sqrt(discriminant)) / 2
"""

import re
import dataclasses
import math

import my_ast
from tokenizer import Tokenizer
import hr

tokenizer = Tokenizer(main_example)
tokenizer.demo(print)


print(tokenizer.token_types)



token_stream = Tokenizer('a = 1')

grammar = """
simple_assign: NAME '=' NUMBER
"""

def parse_simple_assign(tokens):
    name = tokens.read('NAME')
    tokens.read('OP', '=')
    number = tokens.read('NUMBER')
    return my_ast.SimpleAssignment(name.text, int(number.text))

node = parse_simple_assign(token_stream)
my_ast.dump(node)


token_stream = Tokenizer('1 + 3')
token_stream = Tokenizer('10')

grammar = """
simple_addition: NUMBER (+ NUMBER)*
"""

def parse_simple_addition(tokens):
    left = tokens.read('NUMBER')
    left_node = my_ast.Number(int(left.text))
    while True:
        if tokens.try_read('OP', '+'):
            right = tokens.read('NUMBER')
            right_node = my_ast.Number(int(right.text))
            left_node = my_ast.BinOp(left_node, '+', right_node)
        else:
            return left_node

node = parse_simple_addition(token_stream)
print(node)
my_ast.dump(node)

print(node.eval({}))


example = """
a = 1
b = 4
c = 2
"""

grammar = """
simple_assign: NAME '=' NUMBER
program: (NEWLINE | simple_assign NEWLINE)* EOF
"""

def parse_program(tokens):
    # program: (NEWLINE | simple_assign NEWLINE)* EOF
    statements = []
    while True:
        if tokens.try_read('EOF'):
            return my_ast.Program(statements)
        elif tokens.try_read('NEWLINE'):
            pass
        else:
            statement = parse_simple_assign(tokens)
            tokens.read('NEWLINE')
            statements.append(statement)


node = parse_program(Tokenizer(example))
print(node)
my_ast.dump(node)

print('result:', my_ast.exec(node))

grammar = """
program: (NEWLINE | statement NEWLINE)* EOF
statement: if_statement | assignment | ERROR
assignment: expr ['=' expr]
expr: term ('+' term | '-' term)*
term: atom ('*' atom | '/' atom)*
atom: NAME | NUMBER | '(' expr ')' | sqrt
sqrt: SQRT '(' expr ')'
if_statement: IF expr '<' expr ':' statement
"""

def parse_program(tokens):
    # program: (NEWLINE | statement NEWLINE)* EOF
    statements = []
    while True:
        if tokens.try_read('EOF'):
            return my_ast.Program(statements)
        elif tokens.try_read('NEWLINE'):
            pass
        else:
            statement = parse_statement(tokens)
            tokens.read('NEWLINE')
            statements.append(statement)

def parse_statement(tokens):
    if tokens.try_read('ERROR'):
        return my_ast.Error()
    elif tokens.match('IF'):
        return parse_if_statement(tokens)
    else:
        return parse_assignment(tokens)

def parse_assignment(tokens):
    # assignment: expr ['=' expr]
    left = parse_expr(tokens)
    if tokens.try_read('OP', '='):
        right = parse_expr(tokens)
        return my_ast.Assignment(left, right)
    else:
        return left

def parse_expr(tokens):
    # expr: term ('+' term | '-' term)*
    expression = parse_term(tokens)
    while True:
        if tokens.try_read('OP', '+'):
            new_expr = parse_term(tokens)
            expression = my_ast.BinOp(expression, '+', new_expr)
        elif tokens.try_read('OP', '-'):
            new_expr = parse_term(tokens)
            expression = my_ast.BinOp(expression, '-', new_expr)
        else:
            return expression

def parse_term(tokens):
    # term: atom ('*' atom | '/' atom)*
    expression = parse_atom(tokens)
    while True:
        if tokens.try_read('OP', '*'):
            new_expr = parse_atom(tokens)
            expression = my_ast.BinOp(expression, '*', new_expr)
        elif tokens.try_read('OP', '/'):
            new_expr = parse_atom(tokens)
            expression = my_ast.BinOp(expression, '/', new_expr)
        else:
            return expression

def parse_atom(tokens):
    # atom: '(' expr ')' | NAME | NUMBER | sqrt
    if tokens.try_read('OP', '('):
        result = parse_expr(tokens)
        tokens.read('OP', ')')
        return result
    if tokens.match('NUMBER'):
        return my_ast.Number(int(tokens.read().text))
    elif tokens.match('NAME'):
        if tokens.peek().text == 'STOP_HERE':
            raise Error()
        return my_ast.Variable(tokens.read().text)
    elif tokens.match('SQRT'):
        return parse_sqrt(tokens)
    else:
        tokens.raise_syntax_error("Expected '(', name or number")

def parse_if_statement(tokens):
    # if_statement: IF expr '<' expr ':' statement
    tokens.read('IF')
    cond_left = parse_expr(tokens)
    tokens.read('OP', '<')
    cond_right = parse_expr(tokens)
    tokens.read('OP', ':')
    body = parse_statement(tokens)
    cond = my_ast.BinOp(cond_left, '<', cond_right)
    return my_ast.Conditional(cond, body)

def parse_sqrt(tokens):
    # sqrt: SQRT '(' expr ')'
    tokens.read('SQRT')
    tokens.read('OP', '(')
    argument = parse_expr(tokens)
    tokens.read('OP', ')')
    return my_ast.CallFunc(math.sqrt, argument)





node = parse_program(Tokenizer(main_example))
my_ast.dump(node)

print(node)

print(my_ast.exec(node))

