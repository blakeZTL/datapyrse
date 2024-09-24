import pytest
from datapyrse.core.models.column_set import ColumnSet
from datapyrse.core.models.query_expression import QueryExpression


def test_query_expression_no_entity_name():
    with pytest.raises(Exception, match="Entity name is required"):
        QueryExpression(entity_name=None, column_set=None)


def test_query_expression_invalid_entity_name():
    with pytest.raises(Exception, match="Entity name must be a string"):
        QueryExpression(entity_name=123, column_set=None)


def test_query_expression_no_column_set():
    with pytest.raises(Exception, match="Column set is required"):
        QueryExpression(entity_name="test", column_set=None)


def test_query_expression_invalid_column_set():
    with pytest.raises(Exception, match="Column set must be a ColumnSet"):
        QueryExpression(entity_name="test", column_set="invalid")


def test_query_expression_invalid_criteria():
    with pytest.raises(Exception, match="Criteria must be a FilterExpression"):
        QueryExpression(
            entity_name="test", column_set=ColumnSet(True), criteria="invalid"
        )


def test_query_expression_invalid_orders():
    with pytest.raises(Exception, match="Orders must be a list of OrderExpressions"):
        QueryExpression(
            entity_name="test", column_set=ColumnSet(True), orders="invalid"
        )


def test_query_expression_invalid_link_entities():
    with pytest.raises(Exception, match="Link entities must be a list of LinkEntities"):
        QueryExpression(
            entity_name="test", column_set=ColumnSet(True), link_entities="invalid"
        )


def test_query_expression_invalid_top_count():
    with pytest.raises(Exception, match="Top count must be an integer"):
        QueryExpression(
            entity_name="test", column_set=ColumnSet(True), top_count="invalid"
        )

    with pytest.raises(Exception, match="Top count must be greater than 0"):
        QueryExpression(entity_name="test", column_set=ColumnSet(True), top_count=0)


def test_query_expression_invalid_distinct():
    with pytest.raises(Exception, match="Distinct must be a boolean"):
        QueryExpression(
            entity_name="test", column_set=ColumnSet(True), distinct="invalid"
        )


def test_query_expression_to_fetchxml():
    query = QueryExpression(
        entity_name="contact",
        column_set=ColumnSet(True),
        criteria=None,
        orders=[],
        link_entities=[],
        top_count=None,
        distinct=False,
    )

    fetchxml = query.to_fetchxml()

    assert fetchxml == (
        '<fetch version="1.0" outputformat="xml-platform" mapping="logical" distinct="false">'
        '<entity name="contact"><all-attributes /></entity></fetch>'
    )
