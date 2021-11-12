#ifndef COMPILER_JIT_H
#define COMPILER_JIT_H

#include <mlir/ExecutionEngine/ExecutionEngine.h>
#include <mlir/IR/BuiltinOps.h>
#include <mlir/Support/LogicalResult.h>

#include <zamalang/Support/KeySet.h>

namespace mlir {
namespace zamalang {

/// JITLambda is a tool to JIT compile an mlir module and to invoke a function
/// of the module.
class JITLambda {
public:
  class Argument {
  public:
    Argument(KeySet &keySet);
    ~Argument();

    // Create lambda Argument that use the given KeySet to perform encryption
    // and decryption operations.
    static llvm::Expected<std::unique_ptr<Argument>> create(KeySet &keySet);

    // Set a scalar argument at the given pos as a uint64_t.
    llvm::Error setArg(size_t pos, uint64_t arg);

    // Set a argument at the given pos as a 1D tensor of T.
    template <typename T>
    llvm::Error setArg(size_t pos, const T *data, int64_t dim1) {
      return setArg<T>(pos, data, llvm::ArrayRef<int64_t>(&dim1, 1));
    }

    // Set a argument at the given pos as a tensor of T.
    template <typename T>
    llvm::Error setArg(size_t pos, const T *data,
                       llvm::ArrayRef<int64_t> shape) {
      return setArg(pos, 8 * sizeof(T), static_cast<const void *>(data), shape);
    }

    // Get the result at the given pos as an uint64_t.
    llvm::Error getResult(size_t pos, uint64_t &res);

    // Specifies the type of a result
    enum ResultType { SCALAR, TENSOR };

    // Returns the result type at position `pos`. If pos is invalid,
    // an error is returned.
    llvm::Expected<enum ResultType> getResultType(size_t pos);

    // Get a result for tensors, fill the `res` buffer with the value of the
    // tensor result.
    // Returns an error:
    // - if the result is a scalar
    // - or the size of the `res` buffser doesn't match the size of the tensor.
    template <typename T>
    llvm::Error getResult(size_t pos, T *res, size_t size) {
      return std::move(this->getResult(pos, res, sizeof(T), size));
    }

    llvm::Error getResult(size_t pos, void *res, size_t elementSize,
                          size_t numElements);

    // Returns the number of elements of the result vector at position
    // `pos` or an error if the result is a scalar value
    llvm::Expected<size_t> getResultVectorSize(size_t pos);

    // Returns the width of the result scalar at position `pos` or the
    // width of the scalar values of a vector if the result at
    // position `pos` is a tensor.
    llvm::Expected<size_t> getResultWidth(size_t pos);

    // Returns the dimensions of the result tensor at position `pos` or
    // an error if the result is a scalar value
    llvm::Expected<std::vector<int64_t>> getResultDimensions(size_t pos);

  private:
    llvm::Error setArg(size_t pos, size_t width, const void *data,
                       llvm::ArrayRef<int64_t> shape);

    friend JITLambda;
    // Store the pointer on inputs values and outputs values
    std::vector<void *> rawArg;
    // Store the values of inputs
    std::vector<const void *> inputs;
    // Store the values of outputs
    std::vector<void *> outputs;
    // Store the input gates description and the offset of the argument.
    std::vector<std::tuple<CircuitGate, size_t /*offet*/>> inputGates;
    // Store the outputs gates description and the offset of the argument.
    std::vector<std::tuple<CircuitGate, size_t /*offet*/>> outputGates;
    // Store allocated lwe ciphertexts (for free)
    std::vector<LweCiphertext_u64 *> allocatedCiphertexts;
    // Store buffers of ciphertexts
    std::vector<LweCiphertext_u64 **> ciphertextBuffers;

    KeySet &keySet;
  };
  JITLambda(mlir::LLVM::LLVMFunctionType type, llvm::StringRef name)
      : type(type), name(name){};

  /// create a JITLambda that point to the function name of the given module.
  /// Use runtimeLibPath as a shared library if specified.
  static llvm::Expected<std::unique_ptr<JITLambda>>
  create(llvm::StringRef name, mlir::ModuleOp &module,
         llvm::function_ref<llvm::Error(llvm::Module *)> optPipeline,
         llvm::Optional<llvm::StringRef> runtimeLibPath = {});

  /// invokeRaw execute the jit lambda with a list of Argument, the last one is
  /// used to store the result of the computation.
  /// Example:
  /// uin64_t arg0 = 1;
  /// uin64_t res;
  /// llvm::SmallVector<void *> args{&arg1, &res};
  /// lambda.invokeRaw(args);
  llvm::Error invokeRaw(llvm::MutableArrayRef<void *> args);

  /// invoke the jit lambda with the Argument.
  llvm::Error invoke(Argument &args);

private:
  mlir::LLVM::LLVMFunctionType type;
  std::string name;
  std::unique_ptr<mlir::ExecutionEngine> engine;
};

} // namespace zamalang
} // namespace mlir

#endif // COMPILER_JIT_H
