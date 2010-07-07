# Example from http://bjourne.blogspot.com/2007/10/lose-weight-with-min-max-and-clamp.html
def MIN(a, b):
    return (b, a)[a < b]

def MAX(a, b):
    return (b, a)[a > b]

def CLAMP(x, l, h):
    return ((x, l)[x < l], h)[x > h]