// RUN: concretecompiler --passes concrete-to-bconcrete --action=dump-bconcrete %s 2>&1| FileCheck %s

// CHECK-LABEL: func @add_glwe_const_int(%arg0: tensor<1025xi64>) -> tensor<1025xi64>
func @add_glwe_const_int(%arg0: !Concrete.lwe_ciphertext<1024,7>) -> !Concrete.lwe_ciphertext<1024,7> {
  // CHECK-NEXT: %[[V1:.*]] = arith.constant 1 : i8
  // CHECK-NEXT: %[[V2:.*]] = "Concrete.encode_int"(%[[V1]]) : (i8) -> !Concrete.plaintext<8>
  // CHECK-NEXT: %[[V3:.*]] = linalg.init_tensor [1025] : tensor<1025xi64>
  // CHECK-NEXT: "BConcrete.add_plaintext_lwe_buffer"(%1, %arg0, %0) : (tensor<1025xi64>, tensor<1025xi64>, !Concrete.plaintext<8>) -> ()
  // CHECK-NEXT: return %[[V3]] : tensor<1025xi64>
  %0 = arith.constant 1 : i8
  %1 = "Concrete.encode_int"(%0) : (i8) -> !Concrete.plaintext<8>
  %2 = "Concrete.add_plaintext_lwe_ciphertext"(%arg0, %1) : (!Concrete.lwe_ciphertext<1024,7>, !Concrete.plaintext<8>) -> !Concrete.lwe_ciphertext<1024,7>
  return %2 : !Concrete.lwe_ciphertext<1024,7>
}

// CHECK-LABEL: func @add_glwe_int(%arg0: tensor<1025xi64>, %arg1: i5) -> tensor<1025xi64>
func @add_glwe_int(%arg0: !Concrete.lwe_ciphertext<1024,4>, %arg1: i5) -> !Concrete.lwe_ciphertext<1024,4> {
  // CHECK-NEXT: %[[V1:.*]] = "Concrete.encode_int"(%arg1) : (i5) -> !Concrete.plaintext<5>
  // CHECK-NEXT: %[[V2:.*]] = linalg.init_tensor [1025] : tensor<1025xi64>
  // CHECK-NEXT: "BConcrete.add_plaintext_lwe_buffer"(%[[V2:.*]], %arg0, %[[V1:.*]]) : (tensor<1025xi64>, tensor<1025xi64>, !Concrete.plaintext<5>) -> ()
  // CHECK-NEXT: return %[[V2]] : tensor<1025xi64>
  %0 = "Concrete.encode_int"(%arg1) : (i5) -> !Concrete.plaintext<5>
  %1 = "Concrete.add_plaintext_lwe_ciphertext"(%arg0, %0) : (!Concrete.lwe_ciphertext<1024,4>, !Concrete.plaintext<5>) -> !Concrete.lwe_ciphertext<1024,4>
  return %1 : !Concrete.lwe_ciphertext<1024,4>
}
