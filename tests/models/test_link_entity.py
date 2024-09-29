from datapyrse.models.column_set import ColumnSet
from datapyrse.models.link_entity import LinkEntity, JoinOperator
from datapyrse.models.filter_expression import FilterExpression, FilterOperator
from datapyrse.models.condition_expression import (
    ConditionExpression,
    ConditionOperator,
)
import pytest


@pytest.fixture
def filter_expression():
    return FilterExpression(
        filter_operator=FilterOperator.AND,
        conditions=[
            ConditionExpression(
                attribute_name="statuscode",
                operator=ConditionOperator.EQUAL,
                values=1,
            )
        ],
    )


@pytest.fixture
def column_set():
    return ColumnSet(True)


def test_link_entity():
    link_entity = LinkEntity(
        link_from_entity_name="contact",
        link_from_attribute_name="contactid",
        link_to_entity_name="account",
        link_to_attribute_name="accountid",
        join_operator=JoinOperator.INNER,
    )

    assert link_entity.link_from_entity_name == "contact"
    assert link_entity.link_from_attribute_name == "contactid"
    assert link_entity.link_to_entity_name == "account"
    assert link_entity.link_to_attribute_name == "accountid"
    assert link_entity.join_operator == JoinOperator.INNER
    assert link_entity.columns is None
    assert link_entity.link_criteria is None
    assert link_entity.link_entities == []


def test_empty_link_entity_from_name():
    with pytest.raises(ValueError, match="Link from entity name is required"):
        LinkEntity(
            link_from_entity_name=None,
            link_from_attribute_name="accountid",
            link_to_entity_name="contact",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
        )


def test_empty_link_entity_from_attribute():
    with pytest.raises(ValueError, match="Link from attribute name is required"):
        LinkEntity(
            link_from_entity_name="account",
            link_from_attribute_name=None,
            link_to_entity_name="contact",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
        )


def test_empty_link_entity_to_name():
    with pytest.raises(ValueError, match="Link to entity name is required"):
        LinkEntity(
            link_from_entity_name="account",
            link_from_attribute_name="accountid",
            link_to_entity_name=None,
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
        )


def test_empty_link_entity_to_attribute():
    with pytest.raises(ValueError, match="Link to attribute name is required"):
        LinkEntity(
            link_from_entity_name="account",
            link_from_attribute_name="accountid",
            link_to_entity_name="contact",
            link_to_attribute_name=None,
            join_operator=JoinOperator.INNER,
        )


def test_empty_link_entity_join_operator():
    with pytest.raises(ValueError, match="Join operator is required"):
        LinkEntity(
            link_from_entity_name="account",
            link_from_attribute_name="accountid",
            link_to_entity_name="contact",
            link_to_attribute_name="accountid",
            join_operator=None,
        )


def test_invalid_link_entity_join_operator():
    with pytest.raises(ValueError, match="Join operator must be a JoinOperator"):
        LinkEntity(
            link_from_entity_name="account",
            link_from_attribute_name="accountid",
            link_to_entity_name="contact",
            link_to_attribute_name="accountid",
            join_operator="Inner",
        )


def test_link_entity_with_columns(column_set):
    link_entity = LinkEntity(
        link_from_entity_name="contact",
        link_from_attribute_name="contactid",
        link_to_entity_name="account",
        link_to_attribute_name="accountid",
        join_operator=JoinOperator.INNER,
        columns=column_set,
    )

    assert link_entity.columns == column_set


def test_link_entity_with_link_criteria(filter_expression):
    link_entity = LinkEntity(
        link_from_entity_name="contact",
        link_from_attribute_name="contactid",
        link_to_entity_name="account",
        link_to_attribute_name="accountid",
        join_operator=JoinOperator.INNER,
        link_criteria=filter_expression,
    )

    assert link_entity.link_criteria == filter_expression


def test_link_entity_with_link_entities():
    link_entities = [
        LinkEntity(
            link_from_entity_name="contact",
            link_from_attribute_name="contactid",
            link_to_entity_name="account",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
        )
    ]

    link_entity = LinkEntity(
        link_from_entity_name="contact",
        link_from_attribute_name="contactid",
        link_to_entity_name="account",
        link_to_attribute_name="accountid",
        join_operator=JoinOperator.INNER,
        link_entities=link_entities,
    )

    assert link_entity.link_entities == link_entities


def test_invalid_link_entity_columns():
    with pytest.raises(ValueError, match="Columns must be a ColumnSet"):
        LinkEntity(
            link_from_entity_name="contact",
            link_from_attribute_name="contactid",
            link_to_entity_name="account",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
            columns="columns",
        )


def test_invalid_link_entity_link_criteria():
    with pytest.raises(ValueError, match="Link criteria must be a FilterExpression"):
        LinkEntity(
            link_from_entity_name="contact",
            link_from_attribute_name="contactid",
            link_to_entity_name="account",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
            link_criteria="filter_expression",
        )


def test_invalid_link_entity_link_entities():
    with pytest.raises(ValueError, match="Link entities must be a list"):
        LinkEntity(
            link_from_entity_name="contact",
            link_from_attribute_name="contactid",
            link_to_entity_name="account",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
            link_entities="link_entities",
        )
