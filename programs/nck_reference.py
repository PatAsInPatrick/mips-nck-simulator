import sys


def mul(a, b):
    result = 0
    while b != 0:
        result += a
        b -= 1
    return result


def div(a, b):
    q = 0
    while not a < b:
        t = b
        m = 1
        while not a < t + t:
            t = t + t
            m = m + m
        a -= t
        q += m
    return q


def nck(n, k):
    nk = n - k
    a = k if k < nk else nk
    base = n - a
    result = 1
    i = 1
    while not a < i:
        result = mul(result, base + i)
        result = div(result, i)
        i += 1
    return result


def main():
    try:
        data = sys.stdin.read().split()
        n = int(data[0])
        k = int(data[1])
    except (IndexError, ValueError):
        print(-1)
        return
    if n < 1 or 26 < n or k < 0 or n < k:
        print(-1)
    else:
        print(nck(n, k))


main()