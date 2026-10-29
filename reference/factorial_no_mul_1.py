n = 5

fac = 1
for i in range(2,n+1):
    temp = 0
    for j in range(i):
        temp += fac
    fac = temp

print(f"{n}! = {fac}")