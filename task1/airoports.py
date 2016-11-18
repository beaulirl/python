import re
import requests


def read_function():
    r = requests.get('https://wl-prod.sabresonicweb.com/SSW2010/static/22/K6K6/170/templates_/__modules/'
                     'routes/routesModules.js?1478693573776', verify=False)
    d = r.text
    b = d.split('var A')
    parts = b[1].split('},')
    m1 = gen(parts)
    for i in m1:
        print(i)


def gen(text):
    num = 0
    while num < len(text):
        h = re.findall(r'(\w\w\w)[:]', text[num])
        num += 1
        i = 1
        while i < len(h):
            yield h[0] + " - " + h[i]
            i += 1


read_function()

