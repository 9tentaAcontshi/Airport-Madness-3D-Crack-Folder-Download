// RUN: zamacompiler --passes lowlfhe-to-concrete-c-api %s  2>&1| FileCheck %s

// CHECK-LABEL: module
// CHECK-NEXT: func private @add_plaintext_list_glwe_ciphertext_u64(index, !LowLFHE.glwe_ciphertext, !LowLFHE.glwe_ciphertext, !LowLFHE.plaintext_list)
// CHECK-NEXT: func private @fill_plaintext_list_with_expansion_u64(index, !LowLFHE.plaintext_list, !LowLFHE.foreign_plaintext_list)
// CHECK-NEXT: func private @allocate_plaintext_list_u64(index, i32) -> !LowLFHE.plaintext_list
// CHECK-NEXT: func private @allocate_glwe_ciphertext_u64(index, i32, i32) -> !LowLFHE.glwe_ciphertext
// CHECK-NEXT: func private @keyswitch_lwe_u64(index, !LowLFHE.lwe_key_switch_key, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>)
// CHECK-NEXT: func private @getGlobalKeyswitchKey() -> !LowLFHE.lwe_key_switch_key
// CHECK-NEXT: func private @bootstrap_lwe_u64(index, !LowLFHE.lwe_bootstrap_key, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.glwe_ciphertext)
// CHECK-NEXT: func private @getGlobalBootstrapKey() -> !LowLFHE.lwe_bootstrap_key
// CHECK-NEXT: func private @negate_lwe_ciphertext_u64(index, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>)
// CHECK-NEXT: func private @mul_cleartext_lwe_ciphertext_u64(index, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.cleartext<_>)
// CHECK-NEXT: func private @add_plaintext_lwe_ciphertext_u64(index, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.plaintext<_>)
// CHECK-NEXT: func private @add_lwe_ciphertexts_u64(index, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>)
// CHECK-NEXT: func private @allocate_lwe_ciphertext_u64(index, i32) -> !LowLFHE.lwe_ciphertext<_,_>
// CHECK-LABEL: func @keyswitch_lwe(%arg0: !LowLFHE.lwe_ciphertext<1024,4>) -> !LowLFHE.lwe_ciphertext<1024,4>
func @keyswitch_lwe(%arg0: !LowLFHE.lwe_ciphertext<1024,4>) -> !LowLFHE.lwe_ciphertext<1024,4> {
  // CHECK-NEXT: %[[ERR:.*]] = constant 0 : index
  // CHECK-NEXT: %[[C0:.*]] = constant 1 : i32
  // CHECK-NEXT: %[[V1:.*]] = call @allocate_lwe_ciphertext_u64(%[[ERR]], %[[C0]]) : (index, i32) -> !LowLFHE.lwe_ciphertext<_,_>
  // CHECK-NEXT: %[[V2:.*]] = call @getGlobalKeyswitchKey() : () -> !LowLFHE.lwe_key_switch_key
  // CHECK-NEXT: %[[V3:.*]] = unrealized_conversion_cast %arg0 : !LowLFHE.lwe_ciphertext<1024,4> to !LowLFHE.lwe_ciphertext<_,_>
  // CHECK-NEXT: call @keyswitch_lwe_u64(%[[ERR]], %[[V2]], %[[V1]], %[[V3]]) : (index, !LowLFHE.lwe_key_switch_key, !LowLFHE.lwe_ciphertext<_,_>, !LowLFHE.lwe_ciphertext<_,_>) -> ()
  // CHECK-NEXT: %[[RES:.*]] = unrealized_conversion_cast %[[V1]] : !LowLFHE.lwe_ciphertext<_,_> to !LowLFHE.lwe_ciphertext<1024,4>
  // CHECK-NEXT: return %[[RES]] : !LowLFHE.lwe_ciphertext<1024,4>
  %1 = "LowLFHE.keyswitch_lwe"(%arg0) {baseLog = 2 : i32, inputLweSize = 1 : i32, level = 3 : i32, outputLweSize = 1 : i32} : (!LowLFHE.lwe_ciphertext<1024,4>) -> !LowLFHE.lwe_ciphertext<1024,4>
  return %1: !LowLFHE.lwe_ciphertext<1024,4>
}