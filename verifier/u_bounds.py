"""u_bounds.py -- exact recomputation of upper bounds B(n) >= u(n) (maximum number of edges of
a unit-distance graph with n vertices) for 22 <= n <= 52, and of the resulting vertex bounds.

The values B(n) for 32 <= n <= 52 agree with the list of de Grey-Parts (arXiv:2303.14714,
footnote 3): ..., 192, 198, 205, 212, 218, 225, 232, 239, 246, 254 for n = 43, ..., 52.

Inputs (cited, not re-proved here):
  * u(22) <= 61                                   [Alexeev-Mixon-Parshall, arXiv:2412.11914, Sec. 3]
  * Schade's lemma: u(n) <= floor(n u(n-1) / (n-2))   [AMP, Lemma 2]
  * Agoston-Palvolgyi, Prop. 12 (arXiv:2006.06285v3): a unit-distance graph with n vertices,
    m edges and all degrees >= 3 satisfies  n^2 - n >= 4m - 12n + 24 + sum_v C(deg v, 2),
    and sum_v C(deg v, 2) >= J(n, 2m) (balanced degrees). If some degree is <= 2, then
    u(n) <= u(n-1) + 2 [AP, note 6]. Hence u(n) <= max(P(n), B(n-1) + 2).
B(n) = min(Schade bound, AP bound), computed in exact integer arithmetic.
"""
from math import comb


def J(n, S):
    q, r = divmod(S, n)
    return (n - r) * comb(q, 2) + r * comb(q + 1, 2)


def rhs(n, m):
    return 4 * m - 12 * n + 24 + J(n, 2 * m)


def P(n):
    m = 0
    while rhs(n, m + 1) <= n * n - n:
        m += 1
    assert all(rhs(n, k + 1) > rhs(n, k) for k in range(m + 50))   # monotone in m
    return m


def main():
    B = {22: 61}
    print(" n  Schade  AP=max(P,B(n-1)+2)  B(n)   [n^2-n, RHS(P), RHS(P+1)]")
    for n in range(23, 53):
        schade = (n * B[n - 1]) // (n - 2)
        ap = max(P(n), B[n - 1] + 2)
        B[n] = min(schade, ap)
        print(f"{n:3d} {schade:6d} {ap:12d} {B[n]:12d}   [{n * n - n}, {rhs(n, P(n))}, {rhs(n, P(n) + 1)}]")
    assert B[28] == 96 and B[43] == 192 and B[44] == 198
    assert [B[n] for n in range(45, 51)] == [205, 212, 218, 225, 232, 239]   # used in version 2
    assert B[51] == 246 and B[52] == 254
    expected_amp = [61, 66, 72, 78, 84, 90, 96, 103, 110]     # AMP Thm 1(b), n = 22..30
    assert [B[n] for n in range(22, 31)] == expected_amp
    for E, label in ((99, "e5 >= 99"), (193, "e6 >= 193"), (204, "e6 >= 204"), (208, "e6 >= 208"),
                     (235, "e6 >= 235"), (244, "e6 >= 244")):
        v = min(n for n in B if B[n] >= E)
        print(f"  {label} : every graph with <= {v - 1} vertices has <= {B[v - 1]} < {E} edges => v >= {v}")
    print("  OK: u(28) <= 96, u(43) <= 192, u(44) <= 198 ; u(45..50) <= 205, 212, 218, 225, 232, 239 ;"
          " AMP Thm 1(b) reproduced for n = 22..30")


if __name__ == "__main__":
    main()
