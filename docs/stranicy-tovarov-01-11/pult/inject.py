import sys
t = open('template.html', encoding='utf-8').read()
d = open('data.json', encoding='utf-8').read().replace('<\\/', '</').replace('<', '\\u003c')
assert t.count('/*DATA*/') == 1
open(sys.argv[1], 'w', encoding='utf-8').write(t.replace('/*DATA*/', d))
print(len(t.replace('/*DATA*/', d)) // 1024, 'КБ')
