n = int(input("n = "))

fac = 1
i = 2
while i<=n:
    temp = 0
    j=0
    while j<i:
        temp += fac
        j += 1
    fac = temp
    i += 1

print(f"{n}! = {fac}")