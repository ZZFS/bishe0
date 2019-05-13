def triangles():
    l = [1]
    while True:
        yield l
        temp = list()
        temp.append(1)
        i=0
        while i<len(l)-1:
            temp.append(l[i]+l[i+1])
            i += 1
        temp.append(1)
        l=temp


n = 0
results = []
for t in triangles():
    print(t)
    results.append(t)
    n = n + 1
    if n == 10:
        break
