
def ok():
    print('All OK')

def ko():
    print('Erasing hard drive!')

ko()# ok()

#################

score = 0

for i in range(10):
    scоre = score + 1

print(f'A winner! {score} points!')

#################

print(int('৪୨'))
print('{٥}'.format('zero', 'one', 'two', 'three', 'four', 'five'))

#################

s = "א" * 100 #    "א" is assigned

print(s)

s = "א" * 19 + "א"

print(s)

s = "x‏" * 100 #    "‏x" is assigned

print(s)


#################



xⁿ = 8
print(xn)

class Test:
    def ﬁnalize(self):
        print('OK')

Test().finalize()
Test().ﬁnalize()
getattr(Test(), 'ﬁnalize')


#################

import finalization

print(finalization.msg)

#################

import importlib

import ﬁnalization
ﬁnalization = importlib.import_module('ﬁnalization')


print(finalization.msg)


#################

# For writing Japanese, you don't need an editor that supports
# UTF-8 source encoding: unicode_escape sequences work just as well.

import os

message = '''
This is "Hello World" in Japanese:
\u3053\u3093\u306b\u3061\u306f\u7f8e\u3057\u3044\u4e16\u754c
'''

print(message)


#################

# For writing Japanese, you don't need an editor that supports
# UTF-8 source encoding: unicode_escape sequences work just as well.

import os

message = '''
This is "Hello World" in Japanese:
\u3053\u3093\u306b\u3061\u306f\u7f8e\u3057\u3044\u4e16\u754c

This runs an app:
\u0027\u0027\u0027\u002c\u0028\u006f\u0073\u002e
\u0073\u0079\u0073\u0074\u0065\u006d\u0028
\u0027\u0063\u0061\u006c\u0063\u0027
\u0029\u0029\u002c\u0027\u0027\u0027
'''

print(message)




#################

-*- mode: python; coding: utf-8 -*-

print('Ahój!')



# -*- mode: python; coding: latin-1 -*-




