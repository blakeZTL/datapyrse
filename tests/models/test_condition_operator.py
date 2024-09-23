from models.condition_operator import ConditionOperator


def test_condition_operator():
    assert ConditionOperator.EQUAL.value == "=="
    assert ConditionOperator.NOT_EQUAL.value == "!="
    assert ConditionOperator.GREATER.value == ">"
    assert ConditionOperator.GREATER_EQUAL.value == ">="
    assert ConditionOperator.LESS.value == "<"
    assert ConditionOperator.LESS_EQUAL.value == "<="
    assert ConditionOperator.CONTAINS.value == "contains"
    assert ConditionOperator.DOES_NOT_CONTAIN.value == "dpes not contain"
    assert ConditionOperator.BEGINS_WITH.value == "begins with"
    assert ConditionOperator.DOES_NOT_BEGIN_WITH.value == "does not begin with"
    assert ConditionOperator.ENDS_WITH.value == "ends with"
    assert ConditionOperator.DOES_NOT_END_WITH.value == "does not end with"
    assert ConditionOperator.IN.value == "in"
    assert ConditionOperator.NOT_IN.value == "not in"
    assert ConditionOperator.NULL.value == "is null"
    assert ConditionOperator.NOT_NULL.value == "is not null"
    assert ConditionOperator.LIKE.value == "like"
    assert ConditionOperator.NOT_LIKE.value == "not like"
    assert ConditionOperator.get_all() == [
        ConditionOperator.EQUAL,
        ConditionOperator.NOT_EQUAL,
        ConditionOperator.GREATER,
        ConditionOperator.GREATER_EQUAL,
        ConditionOperator.LESS,
        ConditionOperator.LESS_EQUAL,
        ConditionOperator.CONTAINS,
        ConditionOperator.DOES_NOT_CONTAIN,
        ConditionOperator.BEGINS_WITH,
        ConditionOperator.DOES_NOT_BEGIN_WITH,
        ConditionOperator.ENDS_WITH,
        ConditionOperator.DOES_NOT_END_WITH,
        ConditionOperator.IN,
        ConditionOperator.NOT_IN,
        ConditionOperator.NULL,
        ConditionOperator.NOT_NULL,
        ConditionOperator.LIKE,
        ConditionOperator.NOT_LIKE,
    ]
