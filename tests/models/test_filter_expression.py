import pytest
from datapyrse.models.condition_expression import (
    ConditionExpression,
    ConditionOperator,
)
from datapyrse.models.filter_expression import FilterExpression, FilterOperator


@pytest.fixture
def condition_expression():
    return ConditionExpression(
        attribute_name="name", operator=ConditionOperator.EQUAL, values="John"
    )


def test_empty_filter_expression():
    filter_expression = FilterExpression()
    assert filter_expression.filter_operator == FilterOperator.AND
    assert filter_expression.conditions == []
    assert filter_expression.filters == []


def test_filter_expression_with_conditions(condition_expression):
    filter_expression = FilterExpression(conditions=[condition_expression])
    assert filter_expression.conditions == [condition_expression]


def test_filter_expression_with_filters(condition_expression):
    filter_expression = FilterExpression(
        filters=[FilterExpression(conditions=[condition_expression])]
    )
    assert filter_expression.filters == [
        FilterExpression(conditions=[condition_expression])
    ]


def test_filter_expression_with_invalid_filter_operator():
    with pytest.raises(Exception, match="Filter operator must be a FilterOperator"):
        FilterExpression(filter_operator="INVALID")


def test_filter_expression_with_invalid_conditions(condition_expression):
    with pytest.raises(
        Exception, match="Conditions must be a list of ConditionExpressions"
    ):
        FilterExpression(conditions=condition_expression)


def test_filter_expression_with_invalid_filters(condition_expression):
    with pytest.raises(Exception, match="Filters must be a list of FilterExpressions"):
        FilterExpression(filters=condition_expression)
