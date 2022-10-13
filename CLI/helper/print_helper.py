import sys
from tabulate import tabulate # requirements

'''
# Print Helper functionalities
'''

DISABLE_COLOR = False

# Colored strings
RED = '\033[31m'
RED_BOLD = '\033[1;31m'
GREEN = '\033[32m'
GREEN_BOLD = '\033[1;32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
CLEAR = '\033[0m'

# Colors setting

def should_color():
    return not DISABLE_COLOR and sys.stdout.isatty()

def _color(color_code, text):
    return '{0}{1}{2}'.format(color_code, text, CLEAR) if should_color() else text

def red(text):
    return _color(RED, text)

def green(text):
    return _color(GREEN, text)

def yellow(text):
    return _color(YELLOW, text)

def blue(text):
    return _color(BLUE, text)

def magenta(text):
    return _color(MAGENTA, text)

def cyan(text):
    return _color(CYAN, text)


# Text coloring and formatting
def puts(text='', newline=True, stream=sys.stdout.write, border=False):
    if newline:
        text = text + '\n'
    if border:
        table = [[text]]
        output = tabulate(table, tablefmt='grid')
        stream(output)
    else:
        stream(text)

def ok(text):
    puts(green('✔ {0}'.format(text)), border=True)

def warn(text):
    puts(yellow('! {0}'.format(text)), border=True)

def err(text):
    puts(red('✘ {0}'.format(text)), stream=sys.stderr.write, border=True)

def exp(text, stream=sys.stdout.write):
    puts('  ➜ {0}'.format(text), stream=stream)

def err_exp(text):
    exp(text, stream=sys.stderr.write)

def msg(text, stream=sys.stdout.write):
    puts(text, stream=stream)

def color_text(text, color, text1='', text2='', border=False):
    if color == "RED":
        puts(text1 + red('{0}'.format(text)) + text2, border=border)
    elif color == "GREEN":
        puts(text1 + green('{0}'.format(text)) + text2, border=border)
    elif color == "YELLOW":
        puts(text1 + yellow('{0}'.format(text)) + text2, border=border)
    elif color == "BLUE":
        puts(text1 + blue('{0}'.format(text)) + text2, border=border)
    elif color == "MAGENTA":
        puts(text1 + magenta('{0}'.format(text)) + text2, border=border)
    elif color == "CYAN":
        puts(text1 + cyan('{0}'.format(text)) + text2, border=border)

