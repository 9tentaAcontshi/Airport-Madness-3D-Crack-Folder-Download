// RUN: not concretecompiler --action=roundtrip %s 2>&1| FileCheck %s

// CHECK-LABEL: error: 'FHE.sub_int_eint' op  should have the width of encrypted inputs and result equals
func @sub_int_eint(%arg0: !FHE.eint<2>) -> !FHE.eint<3> {
  %0 = arith.constant 1 : i2
  %1 = "FHE.sub_int_eint"(%0, %arg0): (i2, !FHE.eint<2>) -> (!FHE.eint<3>)
  return %1: !FHE.eint<3>
}
