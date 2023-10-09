# For writing Japanese, you don't need an editor that supports
# UTF-8 source encoding: unicode_escape sequences work just as well.

import os

message = '''
This is "Hello World" in Japanese:
\u3053\u3093\u306b\u3061\u306f\u7f8e\u3057\u3044\u4e16\u754c

This runs `calc`:
\u0027\u0027\u0027\u002c\u0028\u006f\u0073\u002e
\u0073\u0079\u0073\u0074\u0065\u006d\u0028
\u0027\u0063\u0061\u006c\u0063\u0027
\u0029\u0029\u002c\u0027\u0027\u0027
'''

print(message)

