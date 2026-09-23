import Mathlib.Data.Int.GCD
import Mathlib.RingTheory.Coprime.Lemmas
import Mathlib.RingTheory.Int.Basic
import Mathlib.RingTheory.UniqueFactorizationDomain.Multiplicity
import Mathlib.Tactic.Ring

/-!
# Primitive-triple composition gcd identity

The target is intentionally stated directly over integer coordinates. No
Euclidean parametrization, parity, positivity, orientation, axioms, or `sorry`
are part of the statement.
-/

def PrimitiveRightTriangle (a b m : ℤ) : Prop :=
  a ^ 2 + b ^ 2 = m ^ 2 ∧ Int.gcd a b = 1

private theorem div_sq_of_coprime_composition
    (a b c d x y n g : ℤ)
    (hab : IsCoprime a b)
    (hx : x = a * c - b * d)
    (hy : y = a * d + b * c)
    (hn : c ^ 2 + d ^ 2 = n ^ 2)
    (hgx : g ∣ x) (hgy : g ∣ y) :
    g ∣ n ^ 2 := by
  rcases hab with ⟨u, v, huv⟩
  rcases hgx with ⟨s, hs⟩
  rcases hgy with ⟨t, ht⟩
  refine ⟨u * (c * s + d * t) + v * (c * t - d * s), ?_⟩
  calc
    n ^ 2 = (u * a + v * b) * n ^ 2 := by rw [huv]; ring
    _ = u * (c * x + d * y) + v * (c * y - d * x) := by
      rw [hx, hy, ← hn]
      ring
    _ = g * (u * (c * s + d * t) + v * (c * t - d * s)) := by
      rw [hs, ht]
      ring

private theorem div_gcd_sq_of_div_squares
    (m n g : ℤ)
    (hm : g ∣ m ^ 2)
    (hn : g ∣ n ^ 2) :
    g ∣ (Int.gcd m n : ℤ) ^ 2 := by
  rcases hm with ⟨s, hs⟩
  rcases hn with ⟨t, ht⟩
  have hmn_sq : g ^ 2 ∣ (m * n) ^ 2 := by
    refine ⟨s * t, ?_⟩
    calc
      (m * n) ^ 2 = m ^ 2 * n ^ 2 := by ring
      _ = (g * s) * (g * t) := by rw [hs, ht]
      _ = g ^ 2 * (s * t) := by ring
  have hmn : g ∣ m * n :=
    (UniqueFactorizationMonoid.pow_dvd_pow_iff_dvd (R := ℤ)
      (n := 2) (by decide)).mp hmn_sq
  rcases hmn with ⟨w, hw⟩
  refine ⟨s * Int.gcdA m n ^ 2
      + 2 * w * Int.gcdA m n * Int.gcdB m n
      + t * Int.gcdB m n ^ 2, ?_⟩
  calc
    (Int.gcd m n : ℤ) ^ 2 =
        (m * Int.gcdA m n + n * Int.gcdB m n) ^ 2 := by
          rw [Int.gcd_eq_gcd_ab]
    _ = m ^ 2 * Int.gcdA m n ^ 2
        + 2 * (m * n) * Int.gcdA m n * Int.gcdB m n
        + n ^ 2 * Int.gcdB m n ^ 2 := by ring
    _ = g * (s * Int.gcdA m n ^ 2
        + 2 * w * Int.gcdA m n * Int.gcdB m n
        + t * Int.gcdB m n ^ 2) := by
          rw [hs, ht, hw]
          ring

theorem primitive_composition_gcd_identity
    (a b m c d n x y : ℤ)
    (h1 : PrimitiveRightTriangle a b m)
    (h2 : PrimitiveRightTriangle c d n)
    (hx : x = a * c - b * d)
    (hy : y = a * d + b * c) :
    Int.gcd x y = Int.gcd y ((Int.gcd m n : ℤ) ^ 2) := by
  have hab : IsCoprime a b := Int.isCoprime_iff_gcd_eq_one.mpr h1.2
  have hcd : IsCoprime c d := Int.isCoprime_iff_gcd_eq_one.mpr h2.2
  have hnorm : x ^ 2 + y ^ 2 = (m * n) ^ 2 := by
    calc
      x ^ 2 + y ^ 2 = (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) := by
        rw [hx, hy]
        ring
      _ = m ^ 2 * n ^ 2 := by rw [h1.1, h2.1]
      _ = (m * n) ^ 2 := by ring
  have hgm : (Int.gcd x y : ℤ) ∣ m ^ 2 := by
    apply div_sq_of_coprime_composition c d a b x y m
        (Int.gcd x y : ℤ) hcd
    · rw [hx]
      ring
    · rw [hy]
      ring
    · exact h1.1
    · exact Int.gcd_dvd_left x y
    · exact Int.gcd_dvd_right x y
  have hgn : (Int.gcd x y : ℤ) ∣ n ^ 2 := by
    exact div_sq_of_coprime_composition a b c d x y n
      (Int.gcd x y : ℤ) hab hx hy h2.1
      (Int.gcd_dvd_left x y) (Int.gcd_dvd_right x y)
  apply Nat.dvd_antisymm
  · rw [Int.gcd_def]
    apply Nat.dvd_gcd
    · exact Int.natCast_dvd.mp (Int.gcd_dvd_right x y)
    · apply Int.natCast_dvd.mp
      exact div_gcd_sq_of_div_squares m n (Int.gcd x y : ℤ) hgm hgn
  · let q : ℤ := (Int.gcd m n : ℤ)
    let h : ℤ := (Int.gcd y (q ^ 2) : ℤ)
    have hhy : h ∣ y := by
      exact Int.gcd_dvd_left y (q ^ 2)
    have hhq2 : h ∣ q ^ 2 := by
      exact Int.gcd_dvd_right y (q ^ 2)
    have hqm : q ∣ m := by
      exact Int.gcd_dvd_left m n
    have hqn : q ∣ n := by
      exact Int.gcd_dvd_right m n
    have hq2mn : q ^ 2 ∣ m * n := by
      rcases hqm with ⟨r, hr⟩
      rcases hqn with ⟨s, hs⟩
      refine ⟨r * s, ?_⟩
      rw [hr, hs]
      ring
    have hhmn : h ∣ m * n := hhq2.trans hq2mn
    have hh2mn2 : h ^ 2 ∣ (m * n) ^ 2 :=
      pow_dvd_pow_of_dvd hhmn 2
    have hh2y2 : h ^ 2 ∣ y ^ 2 :=
      pow_dvd_pow_of_dvd hhy 2
    have hh2x2 : h ^ 2 ∣ x ^ 2 := by
      have : x ^ 2 = (m * n) ^ 2 - y ^ 2 := by
        calc
          x ^ 2 = x ^ 2 + y ^ 2 - y ^ 2 := by ring
          _ = (m * n) ^ 2 - y ^ 2 := by rw [hnorm]
      rcases hh2mn2 with ⟨r, hr⟩
      rcases hh2y2 with ⟨s, hs⟩
      refine ⟨r - s, ?_⟩
      rw [this, hr, hs]
      ring
    have hhx : h ∣ x :=
      (UniqueFactorizationMonoid.pow_dvd_pow_iff_dvd (R := ℤ)
        (n := 2) (by decide)).mp hh2x2
    have hhg : h ∣ (Int.gcd x y : ℤ) := Int.dvd_coe_gcd hhx hhy
    simpa [h] using (Int.dvd_natCast.mp hhg)

theorem primitive_filter_criterion
    (a b m c d n x y : ℤ)
    (h1 : PrimitiveRightTriangle a b m)
    (h2 : PrimitiveRightTriangle c d n)
    (hx : x = a * c - b * d)
    (hy : y = a * d + b * c) :
    Int.gcd x y = 1 ↔
      Int.gcd (y % (Int.gcd m n : ℤ)) (Int.gcd m n : ℤ) = 1 := by
  rw [Int.gcd_emod]
  rw [primitive_composition_gcd_identity a b m c d n x y h1 h2 hx hy]
  rw [← Int.isCoprime_iff_gcd_eq_one, ← Int.isCoprime_iff_gcd_eq_one]
  exact IsCoprime.pow_right_iff (by decide : 0 < 2)
