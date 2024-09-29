import xml.etree.ElementTree as ET
from datapyrse.models.query_expression import QueryExpression
from datapyrse.models.filter_expression import FilterExpression, FilterOperator
from datapyrse.models.link_entity import JoinOperator, LinkEntity
from datapyrse.models.column_set import ColumnSet
from datapyrse.models.order_expression import OrderExpression, OrderType
from datapyrse.models.condition_expression import (
    ConditionExpression,
    ConditionOperator,
)
from datapyrse.utils.query_to_fetch import (
    query_expression_to_fetchxml,
    filter_to_fetchxml,
    link_entity_to_fetchxml,
)


class TestQueryExpressionToFetchXML:

    def test_query_with_columns_and_filter(self):
        query = QueryExpression(
            entity_name="account",
            column_set=ColumnSet(columns=["name", "accountnumber"]),
            criteria=FilterExpression(
                filter_operator=FilterOperator.AND,
                conditions=[
                    ConditionExpression(
                        attribute_name="statuscode",
                        operator=ConditionOperator.EQUAL,
                        values=1,
                    )
                ],
            ),
            orders=[OrderExpression(attribute_name="name", order_type=OrderType.ASC)],
            top_count=50,
        )

        fetchxml = query_expression_to_fetchxml(query)

        root = ET.fromstring(fetchxml)
        entity = root.find("entity")
        if entity is not None:
            assert entity.attrib["name"] == "account"
        else:
            assert False
        assert root.tag == "fetch"
        assert root.attrib["top"] == "50"

        # Check if attributes are correct
        attributes = entity.findall("attribute")
        assert attributes[0].attrib["name"] == "name"
        assert attributes[1].attrib["name"] == "accountnumber"

    def test_query_with_all_attributes(self):
        query = QueryExpression(
            entity_name="account", column_set=ColumnSet(True), orders=[]
        )

        fetchxml = query_expression_to_fetchxml(query)

        root = ET.fromstring(fetchxml)
        entity = root.find("entity")
        all_attributes = entity.find("all-attributes") if entity is not None else None

        assert all_attributes is not None


class TestFilterToFetchXML:

    def test_filter_with_conditions(self):
        filter_expression = FilterExpression(
            filter_operator=FilterOperator.AND,
            conditions=[
                ConditionExpression(
                    attribute_name="statuscode",
                    operator=ConditionOperator.EQUAL,
                    values=1,
                ),
                ConditionExpression(
                    attribute_name="createdon",
                    operator=ConditionOperator.GREATER,
                    values=["2021-01-01"],
                ),
            ],
        )

        filter_xml = filter_to_fetchxml(filter_expression)

        assert filter_xml.tag == "filter"
        assert filter_xml.attrib["type"] == "and"

        conditions = filter_xml.findall("condition")
        assert conditions[0].attrib["attribute"] == "statuscode"
        assert conditions[0].attrib["operator"] == "eq"
        assert conditions[0].attrib["value"] == "1"

        assert conditions[1].attrib["attribute"] == "createdon"
        assert conditions[1].attrib["operator"] == "gt"
        assert conditions[1].attrib["value"] == "2021-01-01"

    def test_nested_filters(self):
        nested_filter = FilterExpression(
            filter_operator=FilterOperator.OR,
            conditions=[
                ConditionExpression(
                    attribute_name="firstname",
                    operator=ConditionOperator.EQUAL,
                    values=["John"],
                )
            ],
        )

        filter_expression = FilterExpression(
            filter_operator=FilterOperator.AND, filters=[nested_filter]
        )

        filter_xml = filter_to_fetchxml(filter_expression)
        nested_filter_xml = filter_xml.find("filter")

        if nested_filter_xml is not None:
            assert nested_filter_xml.attrib["type"] == "or"
        else:
            assert False
        condition = nested_filter_xml.find("condition")
        if condition is not None:
            assert condition.attrib["attribute"] == "firstname"
            assert condition.attrib["operator"] == "eq"
            assert condition.attrib["value"] == "John"
        else:
            assert False


class TestLinkEntityToFetchXML:

    def test_link_entity_with_columns(self):
        link_entity = LinkEntity(
            link_from_entity_name="contact",
            link_from_attribute_name="contactid",
            link_to_entity_name="account",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
            columns=ColumnSet(columns=["name", "accountnumber"]),
        )

        link_xml = link_entity_to_fetchxml(link_entity)

        assert link_xml.tag == "link-entity"
        assert link_xml.attrib["name"] == "account"
        assert link_xml.attrib["from_"] == "contactid"
        assert link_xml.attrib["to"] == "accountid"
        assert link_xml.attrib["linktype"] == "inner"

        attributes = link_xml.findall("attribute")
        assert attributes[0].attrib["name"] == "name"
        assert attributes[1].attrib["name"] == "accountnumber"

    def test_link_entity_with_filter(self):
        link_entity = LinkEntity(
            link_from_entity_name="contact",
            link_from_attribute_name="contactid",
            link_to_entity_name="account",
            link_to_attribute_name="accountid",
            join_operator=JoinOperator.INNER,
            link_criteria=FilterExpression(
                filter_operator=FilterOperator.AND,
                conditions=[
                    ConditionExpression(
                        attribute_name="statuscode",
                        operator=ConditionOperator.EQUAL,
                        values=[1],
                    )
                ],
            ),
        )

        link_xml = link_entity_to_fetchxml(link_entity)

        filter_xml = link_xml.find("filter")
        assert filter_xml is not None
        condition = filter_xml.find("condition")
        assert condition is not None
        assert condition.attrib["attribute"] == "statuscode"
        assert condition.attrib["operator"] == "eq"
        assert condition.attrib["value"] == "1"
