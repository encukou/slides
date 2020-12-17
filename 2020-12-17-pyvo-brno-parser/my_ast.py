import dataclasses
import math


@dataclasses.dataclass
class SimpleAssignment:
    name: str
    number: object

    def __str__(self):
        return f'{self.name} = {self.number}'

    def eval(self, environ):
        environ[self.name] = self.number


def exec(node, env=None):
    """Evaluate `node` and return the resulting environment
    """
    if env is None:
        env = {}
    node.eval(env)
    return env


@dataclasses.dataclass
class Program:
    """A list of statements, executed one after another
    """
    statements: list

    def __str__(self):
        return '\n'.join(str(s) for s in self.statements)

    def eval(self, environ):
        for statement in self.statements:
            statement.eval(environ)


@dataclasses.dataclass
class Assignment:
    """Assigns the value of `value` to the variable in `name`.
    
    `name` must be a Variable.
    """
    name: object
    value: object

    def __str__(self):
        return f'{self.name} = {self.value}'

    def eval(self, environ):
        environ[self.name.name] = self.value.eval(environ)


@dataclasses.dataclass
class Variable:
    """Retrieves the value stored in the given variable
    """
    name: str

    def __str__(self):
        return f'{self.name}'

    def eval(self, environ):
        return environ[self.name]


@dataclasses.dataclass
class Number:
    """Constant integer expression
    """
    value: int

    def __str__(self):
        return f'{self.value}'

    def eval(self, environ):
        return self.value



@dataclasses.dataclass
class BinOp:
    """Evaluates an operation on two operands
    """
    left: object
    op: str
    right: object

    def __str__(self):
        return f'({self.left} {self.op} {self.right})'

    def eval(self, environ):
        left_val = self.left.eval(environ)
        right_val = self.right.eval(environ)
        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            return left_val / right_val
        elif self.op == '<':
            return left_val < right_val
        elif self.op == '>':
            return left_val > right_val
        else:
            raise ValueError(f"unknown operator '{self.op}'")


@dataclasses.dataclass
class Error:
    """Raises an error
    """
    def __str__(self):
        return f'error!'

    def eval(self, environ):
        raise RuntimeError('error!')


@dataclasses.dataclass
class Conditional:
    cond: object
    body: object

    def __str__(self):
        return f'if {self.cond}: {self.body}'

    def eval(self, environ):
        if self.cond.eval(environ):
            self.body.eval(environ)


@dataclasses.dataclass
class CallFunc:
    function: callable
    argument: object

    def __str__(self):
        return f'{self.function.__name__}({self.argument})'

    def eval(self, environ):
        arg_value = self.argument.eval(environ)
        return self.function(arg_value)


def dump(node, indent=0):
    """Print "node" recursively, in a relatively readable way
    """
    print('  ' * indent + type(node).__name__ + '(')
    indent += 1
    for field in dataclasses.fields(node):
        name = field.name
        value = getattr(node, name)
        if dataclasses.is_dataclass(value):
            print('  ' * indent + f'{name}:')
            indent += 1
            dump(value, indent)
            indent -= 1
        elif isinstance(value, list):
            print('  ' * indent + f'{name}=[')
            indent += 1
            for item in value:
                if dataclasses.is_dataclass(item):
                    dump(item, indent)
            indent -= 1
            print('  ' * indent + f']')
        else:
            print('  ' * indent + f'{name}: {value!r}')
    indent -= 1
    print('  ' * indent + ')')

