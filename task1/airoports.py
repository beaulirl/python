import re


def read_function(filename):
    f = open(filename, 'rU')
    s = f.read()
    b = s.split('var A')
    parts = b[1].split('},')
    m = 0
    while m < len(parts):
        h = re.findall(r'(\w\w\w)[:]', parts[m])
        m += 1
        i = 1
        while i < len(h):
            print(h[0], "-", h[i])
            i += 1

read_function("18_Full.txt")

