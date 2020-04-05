

domainss = [[[1,2,3,4,5,6,7,8,9] for x in range(9)] for y in range(9)]


def updateDomains(j, i, value, domains):
    f = lambda x: int(x / 3) * 3
    doms = domains[:]
    for dom in doms[j][:]:
        print(dom, end=': dom\n')
        if dom != doms[j][i] and value in dom:
            print('removing')
            dom.remove(value)

    for dom in doms[:][i]:
        print(dom, end=': dom\n')
        if dom != doms[j][i] and value in dom:
            print('removing')
            dom.remove(value)

    """for dom in doms[f(j):f(j) + 3][f(i):f(i) + 3]:
        print(dom, end=': dom3\n')
        if dom != doms[j][i] and value in dom:
            print('removing')
            dom.remove(value)"""
    return doms


f = lambda x: int(x / 3) * 3

print(domainss[f(5):f(5) + 3][f(5):f(5) + 3])

print('First loop')
for doms in domainss[5][:]:
    print(doms)
print('Sec loop')
for doms in domainss[:][5]:
    print(doms)
"""print('3th loop')
for dom in doms[f(5):f(5) + 3][f(5):f(5) + 3]:
    print(doms)"""

domainss = updateDomains(5, 5, 3, domainss)

print('First loop')
for doms in domainss[5][:]:
    print(doms)
print('Sec loop')
for doms in domainss[:][5]:
    print(doms)
"""print('3th loop')
for dom in doms[f(5):f(5) + 3][f(5):f(5) + 3]:
    print(doms)"""