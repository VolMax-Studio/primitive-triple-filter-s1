import PrimitiveTripleFilter
import Mathlib.Tactic.NormNum.GCD

/-!
# Complete-cancellation sanity test

For `(3 + 4i)(3 - 4i) = 25 + 0i`, the identity and modular criterion must both
cover the zero imaginary coordinate without an added `y ≠ 0` hypothesis.
-/

example :
    Int.gcd (25 : ℤ) 0 =
      Int.gcd 0 ((Int.gcd (5 : ℤ) 5 : ℤ) ^ 2) := by
  exact primitive_composition_gcd_identity
    (3 : ℤ) 4 5 3 (-4) 5 25 0
    (by norm_num [PrimitiveRightTriangle])
    (by norm_num [PrimitiveRightTriangle])
    (by norm_num)
    (by norm_num)

example :
    Int.gcd (25 : ℤ) 0 = 1 ↔
      Int.gcd (0 % (Int.gcd (5 : ℤ) 5 : ℤ)) (Int.gcd (5 : ℤ) 5 : ℤ) = 1 := by
  exact primitive_filter_criterion
    (3 : ℤ) 4 5 3 (-4) 5 25 0
    (by norm_num [PrimitiveRightTriangle])
    (by norm_num [PrimitiveRightTriangle])
    (by norm_num)
    (by norm_num)
