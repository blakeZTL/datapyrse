# pylint: disable=missing-function-docstring, missing-module-docstring

import pytest
from datapyrse.query import (
    ConditionExpression,
    ConditionOperator,
)


def test_condition_expression():
    condition_expression = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.EQUAL, value="John"
    )
    assert condition_expression.attribute_name == "name"
    assert condition_expression.operator == ConditionOperator.EQUAL
    assert condition_expression.value == ["John"]


def test_condition_expression_with_no_value():
    condition_expression = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.NULL, value=None
    )
    assert condition_expression.attribute_name == "name"
    assert condition_expression.operator == ConditionOperator.NULL
    assert condition_expression.value is None


def test_condition_expression_with_no_operator():
    try:
        ConditionExpression(attribute_name="name", operator=None, value=["John"])  # type: ignore
    except ValueError as e:
        assert str(e) == "Operator is required"


def test_condition_expression_with_invalid_operator():
    pytest.raises(
        ValueError,
        ConditionExpression,
        "name",
        "invalid_operator",
        ["John"],
    )


def test_condition_expression_with_no_attribute_name():
    try:
        ConditionExpression(
            attribute_name="", operator=ConditionOperator.EQUAL, value=["John"]
        )
    except ValueError as e:
        assert str(e) == "Attribute name is required"


def test_condition_expression_with_invalid_value_type():
    pytest.raises(
        ValueError,
        ConditionExpression,
        "name",
        ConditionOperator.EQUAL,
        {"name": "John"},
    )


def test_condition_expression_with_single_value_should_return_list():
    con_ex = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.EQUAL, value="John"
    )
    assert con_ex.value == ["John"]

    con_ex = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.EQUAL, value=["John"]
    )
    assert con_ex.value == ["John"]

    con_ex = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.EQUAL, value=[1]
    )
    assert con_ex.value == [1]


@pytest.mark.parametrize(
    "operator", [ConditionOperator.NULL, ConditionOperator.NOT_NULL]
)
def test_condition_expression_with_null_operator_and_value(operator: ConditionOperator):
    con_ex = ConditionExpression(
        attribute_name="name", operator=operator, value=["John"]
    )
    assert con_ex.value is None


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_no_value(operator: ConditionOperator):
    pytest.raises(ValueError, ConditionExpression, "name", operator, None)


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_not_list(operator: ConditionOperator):
    try:
        ConditionExpression(attribute_name="name", operator=operator, value="John")
    except ValueError as e:
        assert str(e) == "value must be a list for IN/NOT IN operators"


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_empty_list(operator: ConditionOperator):
    pytest.raises(ValueError, ConditionExpression, "name", operator, [])


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_too_many_value(
    operator: ConditionOperator,
):
    pytest.raises(
        ValueError, ConditionExpression, "name", operator, ["John", "Doe"] * 500
    )
