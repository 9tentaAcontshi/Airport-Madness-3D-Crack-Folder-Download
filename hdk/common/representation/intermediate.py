"""File containing code to represent source programs operations."""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Type

from ..data_types.base import BaseDataType
from ..data_types.dtypes_helpers import (
    get_base_value_for_python_constant_data,
    mix_scalar_values_determine_holding_dtype,
)
from ..values import BaseValue, ClearValue, EncryptedValue, TensorValue

IR_MIX_VALUES_FUNC_ARG_NAME = "mix_values_func"

ALL_IR_NODES: Set[Type] = set()


class IntermediateNode(ABC):
    """Abstract Base Class to derive from to represent source program operations."""

    inputs: List[BaseValue]
    outputs: List[BaseValue]
    _n_in: int  # _n_in indicates how many inputs are required to evaluate the IntermediateNode

    def __init__(
        self,
        inputs: Iterable[BaseValue],
        **_kwargs,  # This is to be able to feed arbitrary arguments to IntermediateNodes
    ) -> None:
        self.inputs = list(inputs)
        assert all(isinstance(x, BaseValue) for x in self.inputs)

    # Register all IR nodes
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ALL_IR_NODES.add(cls)

    def _init_binary(
        self,
        inputs: Iterable[BaseValue],
        mix_values_func: Callable[..., BaseValue] = mix_scalar_values_determine_holding_dtype,
        **_kwargs,  # Required to conform to __init__ typing
    ) -> None:
        """__init__ for a binary operation, ie two inputs."""
        IntermediateNode.__init__(self, inputs)

        assert len(self.inputs) == 2

        self.outputs = [mix_values_func(self.inputs[0], self.inputs[1])]

    def _is_equivalent_to_binary_commutative(self, other: object) -> bool:
        """is_equivalent_to for a binary and commutative operation."""
        return (
            isinstance(other, self.__class__)
            and (self.inputs == other.inputs or self.inputs == other.inputs[::-1])
            and self.outputs == other.outputs
        )

    def _is_equivalent_to_binary_non_commutative(self, other: object) -> bool:
        """is_equivalent_to for a binary and non-commutative operation."""
        return (
            isinstance(other, self.__class__)
            and self.inputs == other.inputs
            and self.outputs == other.outputs
        )

    @abstractmethod
    def is_equivalent_to(self, other: object) -> bool:
        """Alternative to __eq__ to check equivalence between IntermediateNodes.

        Overriding __eq__ has unwanted side effects, this provides the same facility without
        disrupting expected behavior too much

        Args:
            other (object): Other object to check against

        Returns:
            bool: True if the other object is equivalent
        """
        return (
            isinstance(other, IntermediateNode)
            and self.inputs == other.inputs
            and self.outputs == other.outputs
        )

    @abstractmethod
    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        """Function to simulate what the represented computation would output for the given inputs.

        Args:
            inputs (Dict[int, Any]): Dict containing the inputs for the evaluation

        Returns:
            Any: the result of the computation
        """

    @classmethod
    def n_in(cls) -> int:
        """Returns how many inputs the node has.

        Returns:
            int: The number of inputs of the node.
        """
        return cls._n_in

    @classmethod
    def requires_mix_values_func(cls) -> bool:
        """Function to determine whether the Class requires a mix_values_func to be built.

        Returns:
            bool: True if __init__ expects a mix_values_func argument.
        """
        return cls.n_in() > 1

    @abstractmethod
    def label(self) -> str:
        """Function to get the label of the node.

        Returns:
            str: the label of the node

        """


class Add(IntermediateNode):
    """Addition between two values."""

    _n_in: int = 2

    __init__ = IntermediateNode._init_binary
    is_equivalent_to = IntermediateNode._is_equivalent_to_binary_commutative

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        return inputs[0] + inputs[1]

    def label(self) -> str:
        return "+"


class Sub(IntermediateNode):
    """Subtraction between two values."""

    _n_in: int = 2

    __init__ = IntermediateNode._init_binary
    is_equivalent_to = IntermediateNode._is_equivalent_to_binary_non_commutative

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        return inputs[0] - inputs[1]

    def label(self) -> str:
        return "-"


class Mul(IntermediateNode):
    """Multiplication between two values."""

    _n_in: int = 2

    __init__ = IntermediateNode._init_binary
    is_equivalent_to = IntermediateNode._is_equivalent_to_binary_commutative

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        return inputs[0] * inputs[1]

    def label(self) -> str:
        return "*"


class Input(IntermediateNode):
    """Node representing an input of the program."""

    input_name: str
    program_input_idx: int
    _n_in: int = 1

    def __init__(
        self,
        input_value: BaseValue,
        input_name: str,
        program_input_idx: int,
    ) -> None:
        super().__init__((input_value,))
        assert len(self.inputs) == 1
        self.input_name = input_name
        self.program_input_idx = program_input_idx
        self.outputs = [deepcopy(self.inputs[0])]

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        return inputs[0]

    def is_equivalent_to(self, other: object) -> bool:
        return (
            isinstance(other, Input)
            and self.input_name == other.input_name
            and self.program_input_idx == other.program_input_idx
            and super().is_equivalent_to(other)
        )

    def label(self) -> str:
        return self.input_name


class Constant(IntermediateNode):
    """Node representing a constant of the program."""

    _constant_data: Any
    _n_in: int = 0

    def __init__(
        self,
        constant_data: Any,
        get_base_value_for_data_func: Callable[
            [Any], Callable[..., BaseValue]
        ] = get_base_value_for_python_constant_data,
    ) -> None:
        super().__init__([])

        base_value_class = get_base_value_for_data_func(constant_data)

        self._constant_data = constant_data
        self.outputs = [base_value_class(is_encrypted=False)]

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        return self.constant_data

    def is_equivalent_to(self, other: object) -> bool:
        return (
            isinstance(other, Constant)
            and self.constant_data == other.constant_data
            and super().is_equivalent_to(other)
        )

    @property
    def constant_data(self) -> Any:
        """Returns the constant_data stored in the Constant node.

        Returns:
            Any: The constant data that was stored.
        """
        return self._constant_data

    def label(self) -> str:
        return str(self.constant_data)


class ArbitraryFunction(IntermediateNode):
    """Node representing a univariate arbitrary function, e.g. sin(x)."""

    # The arbitrary_func is not optional but mypy has a long standing bug and is not able to
    # understand this properly. See https://github.com/python/mypy/issues/708#issuecomment-605636623
    arbitrary_func: Optional[Callable]
    op_args: Tuple[Any, ...]
    op_kwargs: Dict[str, Any]
    op_name: str
    _n_in: int = 1

    def __init__(
        self,
        input_base_value: BaseValue,
        arbitrary_func: Callable,
        output_dtype: BaseDataType,
        op_name: Optional[str] = None,
        op_args: Optional[Tuple[Any, ...]] = None,
        op_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__([input_base_value])
        assert len(self.inputs) == 1
        self.arbitrary_func = arbitrary_func
        self.op_args = op_args if op_args is not None else ()
        self.op_kwargs = op_kwargs if op_kwargs is not None else {}
        self.outputs = [input_base_value.__class__(output_dtype, input_base_value.is_encrypted)]
        self.op_name = op_name if op_name is not None else self.__class__.__name__

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        # This is the continuation of the mypy bug workaround
        assert self.arbitrary_func is not None
        return self.arbitrary_func(inputs[0], *self.op_args, **self.op_kwargs)

    def is_equivalent_to(self, other: object) -> bool:
        # FIXME: comparing self.arbitrary_func to other.arbitrary_func will not work
        # Only evaluating over the same set of inputs and comparing will help
        return (
            isinstance(other, ArbitraryFunction)
            and self.op_args == other.op_args
            and self.op_kwargs == other.op_kwargs
            and self.op_name == other.op_name
            and super().is_equivalent_to(other)
        )

    def label(self) -> str:
        return self.op_name


def default_dot_evaluation_function(lhs: Any, rhs: Any) -> Any:
    """Default python dot implementation for 1D iterable arrays.

    Args:
        lhs (Any): lhs vector of the dot.
        rhs (Any): rhs vector of the dot.

    Returns:
        Any: the result of the dot operation.
    """
    return sum(lhs * rhs for lhs, rhs in zip(lhs, rhs))


class Dot(IntermediateNode):
    """Node representing a dot product."""

    _n_in: int = 2
    # Optional, same issue as in ArbitraryFunction for mypy
    evaluation_function: Optional[Callable[[Any, Any], Any]]
    # Allows to use specialized implementations from e.g. numpy

    def __init__(
        self,
        inputs: Iterable[BaseValue],
        output_dtype: BaseDataType,
        delegate_evaluation_function: Optional[
            Callable[[Any, Any], Any]
        ] = default_dot_evaluation_function,
    ) -> None:
        super().__init__(inputs)
        assert len(self.inputs) == 2

        assert all(
            isinstance(input_value, TensorValue) and input_value.ndim == 1
            for input_value in self.inputs
        ), f"Dot only supports two vectors ({TensorValue.__name__} with ndim == 1)"

        output_scalar_value = (
            EncryptedValue
            if (self.inputs[0].is_encrypted or self.inputs[1].is_encrypted)
            else ClearValue
        )

        self.outputs = [output_scalar_value(output_dtype)]
        self.evaluation_function = delegate_evaluation_function

    def evaluate(self, inputs: Dict[int, Any]) -> Any:
        # This is the continuation of the mypy bug workaround
        assert self.evaluation_function is not None
        return self.evaluation_function(inputs[0], inputs[1])

    def is_equivalent_to(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.evaluation_function == other.evaluation_function
            and super().is_equivalent_to(other)
        )

    # TODO: Coverage will come with the ability to trace the operator in a subsequent PR
    def label(self) -> str:  # pragma: no cover
        return "dot"
