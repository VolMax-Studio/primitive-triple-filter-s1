#!/usr/bin/env python3
"""Exploratory finite check of the exact gcd identity; never uses the benchmark seed."""

import json
from math import gcd, isqrt


def primitive_triples(max_hypotenuse=1000):
    triples = {(1, 0, 1), (0, 1, 1), (-1, 0, 1), (0, -1, 1)}
    for u in range(2, isqrt(max_hypotenuse) + 2):
        for v in range(1, u):
            if gcd(u, v) != 1 or (u - v) % 2 != 1:
                continue
            a, b, m = u * u - v * v, 2 * u * v, u * u + v * v
            if m > max_hypotenuse:
                continue
            for left, right in ((a, b), (b, a), (-a, b), (a, -b)):
                triples.add((left, right, m))
    return sorted(triples)


def main():
    triples = primitive_triples()
    assert all(a*a + b*b == m*m and gcd(a, b) == 1 for a, b, m in triples)
    checked = shared_hypotenuse = nonprimitive_products = 0
    for a, b, m in triples:
        for c, d, n in triples:
            x, y, q = a*c - b*d, a*d + b*c, gcd(m, n)
            actual = gcd(x, y)
            predicted = gcd(y, q*q)
            if actual != predicted or (actual == 1) != (gcd(y, q) == 1):
                raise AssertionError((a, b, m, c, d, n, x, y, q, actual, predicted))
            checked += 1
            shared_hypotenuse += q > 1
            nonprimitive_products += actual > 1
    print(json.dumps({
        "status": "FINITE_CHECK_ONLY_NOT_LEAN_PROOF",
        "max_hypotenuse": 1000,
        "primitive_signed_oriented_triples": len(triples),
        "ordered_compositions": checked,
        "shared_hypotenuse_factor": shared_hypotenuse,
        "nonprimitive_products": nonprimitive_products,
        "mismatches": 0,
        "candidate_identity": "gcd(x,y) = gcd(y,gcd(m,n)^2)",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
