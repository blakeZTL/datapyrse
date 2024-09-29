import pytest
from datapyrse.models.condition_expression import (
    ConditionExpression,
    ConditionOperator,
)


def test_condition_expression():
    condition_expression = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.EQUAL, values="John"
    )
    assert condition_expression.attribute_name == "name"
    assert condition_expression.operator == ConditionOperator.EQUAL
    assert condition_expression.values == ["John"]


def test_condition_expression_with_no_values():
    condition_expression = ConditionExpression(
        attribute_name="name", operator=ConditionOperator.NULL, values=None
    )
    assert condition_expression.attribute_name == "name"
    assert condition_expression.operator == ConditionOperator.NULL
    assert condition_expression.values == None


def test_condition_expression_with_no_operator():
    try:
        ConditionExpression(attribute_name="name", operator=None, values=["John"])  # type: ignore
    except Exception as e:
        assert str(e) == "Operator is required"


def test_condition_expression_with_no_attribute_name():
    try:
        ConditionExpression(
            attribute_name="", operator=ConditionOperator.EQUAL, values=["John"]
        )
    except Exception as e:
        assert str(e) == "Attribute name is required"


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_no_values(operator):
    try:
        ConditionExpression(attribute_name="name", operator=operator, values=None)
    except Exception as e:
        assert str(e) == "Values are required for IN/NOT IN operators"


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_not_list(operator):
    try:
        ConditionExpression(attribute_name="name", operator=operator, values="John")
    except Exception as e:
        assert str(e) == "Values must be a list for IN/NOT IN operators"


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_empty_list(operator):
    try:
        ConditionExpression(attribute_name="name", operator=operator, values=[])
    except Exception as e:
        assert str(e) == "Values are required for IN/NOT IN operators"


@pytest.mark.parametrize("operator", [ConditionOperator.IN, ConditionOperator.NOT_IN])
def test_condition_expression_with_in_operator_too_many_values(operator):
    try:
        ConditionExpression(attribute_name="name", operator=operator, values=[1] * 501)
    except Exception as e:
        assert (
            str(e) == "Values must contain less than 500 values for IN/NOT IN operators"
        )


def test_condition_expression_with_invalid_attribute_name():
    try:
        ConditionExpression(
            attribute_name=1, operator=ConditionOperator.EQUAL, values="John"  # type: ignore
        )
    except Exception as e:
        assert str(e) == "Attribute name must be a string"


def test_condition_expression_with_invalid_operator():
    try:
        ConditionExpression(attribute_name="name", operator="invalid", values="John")  # type: ignore
    except Exception as e:
        assert str(e) == "Operator must be a ConditionOperator"


def test_condition_expression_with_invalid_values():
    try:
        ConditionExpression(
            attribute_name="name",
            operator=ConditionOperator.EQUAL,
            values=[],
        )
    except Exception as e:
        assert str(e) == "Values must be a list for IN/NOT IN operators"
