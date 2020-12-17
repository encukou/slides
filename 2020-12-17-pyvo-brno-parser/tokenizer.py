import dataclasses
import re


@dataclasses.dataclass
class Token:
    name: str
    text: str
    line: int
    column: int

    def matches(self, name=None, text=None):
        if name and self.name != name:
            return False
        if text and self.text != text:
            return False
        return True

    def __str__(self):
        text = self.text
        if self.matches('NEWLINE'):
            text = text.replace('\n', '\\n')
        return f'{self.line}:{self.column}\t{self.name}\t{text}'



DEFAULT_RULES = {
    None: r' +|#[^\n]*',  # spaces and comments
    'NEWLINE': r'\n+',
    'IF': r'if\b',
    'SQRT': r'sqrt\b',
    'ERROR': r'error!',
    'NAME': r'[a-zA-Z_]+[a-z0-9A-Z_]*',
    'NUMBER': r'-?[0-9]+',
    'OP': r'[():<>=*/+-]',
}


class Tokenizer:
    """Stream of tokens for a LL(1) parser.

    Provides methods to examine the next token to be read, and to read it
    (advance to the next token).

    Tokenizer objects are also iterable.
    """

    def __init__(self, source, rules=DEFAULT_RULES):
        self.source = source
        self.rules = dict(rules)
        self.next_token = None
        self.generator = self._tokenize()
        # Info for nicer error messages:
        self.line_number = 1
        self.column_number = 1
        self.lines = [''] + source.splitlines()

    def peek(self, *match_args, **match_kwargs):
        """Return the next token to be read"""
        if not self.next_token:
            #print('READ',             self.next_token)
            self.next_token = next(self.generator)
        return self.next_token

    def match(self, *match_args, **match_kwargs):
        """Return True if the next token matches the given arguments"""
        token = self.peek()
        return token.matches(*match_args, **match_kwargs)

    def expect(self, *match_args, **match_kwargs):
        """Raise SyntaxError if the next token doesn't match given arguments"""
        token = self.peek()
        if not token.matches(*match_args, **match_kwargs):
            exp = ' '.join(
                v for v
                in match_args +
                    tuple(f'{k}={v!r}' for k, v in match_kwargs.items())
                if v
            )
            raise self.raise_syntax_error(f'Expected {exp}')
        return token

    def read(self, *match_args, **match_kwargs):
        """Return the next token and advance to the next token

        Raise SyntaxError if the token doesn't match.
        """
        result = self.expect(*match_args, **match_kwargs)
        self.next_token = None
        return result

    def try_read(self, *match_args, **match_kwargs):
        """read() if the next token matches the given arguments

        Do nothing if it does not match.
        """
        if self.match(*match_args, **match_kwargs):
            return self.read()

    def raise_syntax_error(self, message='Invalid syntax'):
        """Raise SyntaxError at the given position in the file"""
        at = f'at line {self.line_number}:'
        line = self.lines[self.line_number]
        marker = ' ' * self.column_number + '^'
        raise SyntaxError(f'{message}\n{at}\n    {line}\n    {marker}')

    @property
    def token_types(self):
        return [t for t in self.rules if t]

    def _make_token(self, name, text):
        """Make a token with the current line/column position"""
        return Token(name, text, self.line_number, self.column_number)

    def _tokenize(self):
        """The main generator of tokens"""
        while self.source:
            for name, expression in self.rules.items():
                if match := re.match(expression, self.source, re.MULTILINE):
                    token_text = match[0]

                    # The following line is inefficient for long programs;
                    # it would be better (but more complex) to read the source
                    # line by line
                    self.source = self.source[len(token_text):]

                    if name:
                        yield self._make_token(name, token_text)
                    self._advance_position(token_text)
                    break
            else:
                raise self.raise_syntax_error()
        yield self._make_token('EOF', '')

    def _advance_position(self, token_text):
        """Advance the current line/column position"""
        if '\n' in token_text:
            self.line_number += token_text.count('\n')
            self.column_number = 1
        self.column_number += len(token_text.rpartition('\n')[-1])

    def __iter__(self):
        while True:
            token = self.read()
            yield token
            if token.name == 'EOF':
                break

    def demo(self, pause_func=print):
        print('pos name text'.replace(' ', '\t'))
        print('--------------------')
        for token in self:
            print(token)
            if token.matches('NEWLINE'):
                pause_func()
            if token.matches('EOF'):
                break
        print()

