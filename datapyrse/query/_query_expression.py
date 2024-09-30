""" A module for creating query expressions for queries """

from dataclasses import dataclass, field
from typing import Optional
import xml.etree.ElementTree as ET

from datapyrse.query._condition_expression import ConditionOperator
from datapyrse.query._filter_expression import FilterExpression
from datapyrse.query._link_entity import LinkEntity
from datapyrse.query._order_expression import OrderExpression
from datapyrse.query._column_set import ColumnSet


@dataclass
class QueryExpression:
    """
    Represents a query expression in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of a query expression
    object in Dataverse, including the entity name, column set, criteria, orders,
    link entities, top count, and distinct flag.

    Attributes:
        entity_name (str): The name of the entity to query.
        column_set (ColumnSet): The columns to include in the query.
        criteria (Optional[FilterExpression]): The criteria to apply to the query.
        orders (Optional[list[OrderExpression]]): The order expressions to apply to the query.
        link_entities (Optional[list[LinkEntity]]): The link entities to include in the query.
        top_count (Optional[int]): The maximum number of records to return.
        distinct (bool): A flag indicating whether to return distinct records.
        fetch_xml (str): The FetchXML representation of the query that is generated.

    Raises:
        ValueError: If entity_name or column_set are not provided.
    """

    entity_name: str
    column_set: ColumnSet
    criteria: Optional[FilterExpression] = None
    orders: Optional[list[OrderExpression]] = field(default_factory=list)
    link_entities: Optional[list[LinkEntity]] = field(default_factory=list)
    top_count: Optional[int] = None
    distinct: bool = False
    fetch_xml: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.entity_name:
            raise ValueError("Entity name is required")

        if not self.column_set:
            raise ValueError("Column set is required")

        if self.top_count is not None:
            if self.top_count < 1:
                raise ValueError("Top count must be greater than 0")
        self.fetch_xml = _query_expression_to_fetchxml(self)


def _query_expression_to_fetchxml(query: QueryExpression) -> str:
    """
    Convert a QueryExpression object to a FetchXML string

    Args:
        query (QueryExpression): The QueryExpression object to convert

    Returns:
        str: The FetchXML string representing the QueryExpression
    """
    # Root element: <fetch>
    fetch = ET.Element(
        "fetch",
        version="1.0",
        outputformat="xml-platform",
        mapping="logical",
        distinct=str(query.distinct).lower(),
    )

    if query.top_count:
        fetch.set("top", str(query.top_count))

    # <entity> element with entity name
    entity = ET.SubElement(fetch, "entity", name=query.entity_name)

    # Columns/attributes
    if not isinstance(query.column_set.columns, list):
        raise ValueError("Columns must be a list of strings")
    if query.column_set.columns == []:
        ET.SubElement(entity, "all-attributes")
    else:
        for column in query.column_set.columns:
            ET.SubElement(entity, "attribute", name=column)

    # Add filters (if any)
    if query.criteria:
        entity.append(_filter_to_fetchxml(query.criteria))

    # Add orders (if any)
    if query.orders:
        for order in query.orders:
            ET.SubElement(
                entity,
                "order",
                attribute=order.attribute_name,
                descending=("true" if order.order_type == "DESC" else "false"),
            )

    # Add linked entities (if any)
    if query.link_entities:
        for link_entity in query.link_entities:
            entity.append(_link_entity_to_fetchxml(link_entity))

    # Convert the XML tree to a string
    return ET.tostring(fetch, encoding="unicode")


def _filter_to_fetchxml(filter_expression: FilterExpression) -> ET.Element:
    """
    Convert a FilterExpression object to an XML element for FetchXML

    Args:
        filter_expression (FilterExpression): The FilterExpression object to convert

    Returns:
        ET.Element: The XML element representing the FilterExpression
    """
    filter_element = ET.Element(
        "filter", type=filter_expression.filter_operator.value.lower()
    )

    # Add conditions
    for condition in filter_expression.conditions:
        condition_element = ET.SubElement(
            filter_element,
            "condition",
            attribute=condition.attribute_name,
            operator=condition.operator.value.lower(),
            value="",
        )
        if (
            (condition.operator in [ConditionOperator.IN, ConditionOperator.NOT_IN])
            and condition.value
            and isinstance(condition.value, list)
        ):
            for value in condition.value:
                value_element = ET.SubElement(condition_element, "value")
                value_element.text = str(value)
        elif not isinstance(condition.value, list):
            condition_element.set("value", str(condition.value))
        elif len(condition.value) == 1:
            condition_element.set("value", str(condition.value[0]))
        else:
            raise ValueError(
                "Condition value can only be a list of length more than one for IN and NOT IN operators"
            )

    # Add nested filters (if any)
    for sub_filter in filter_expression.filters:
        filter_element.append(_filter_to_fetchxml(sub_filter))

    return filter_element


def _link_entity_to_fetchxml(link_entity: LinkEntity) -> ET.Element:
    """
    Convert a LinkEntity object to an XML element for FetchXML

    Args:
        link_entity (LinkEntity): The LinkEntity object to convert

    Returns:
        ET.Element: The XML element representing the LinkEntity
    """

    link_element = ET.Element(
        "link-entity",
        name=link_entity.link_to_entity_name,
        from_=link_entity.link_from_attribute_name,
        to=link_entity.link_to_attribute_name,
        linktype=link_entity.join_operator.value.lower(),
    )

    # Add linked entity columns (if any)
    if link_entity.columns:
        if (
            isinstance(link_entity.columns.columns, bool)
            and link_entity.columns.columns is True
        ):
            ET.SubElement(link_element, "all-attributes")
        elif isinstance(link_entity.columns.columns, list):
            for column in link_entity.columns.columns:
                ET.SubElement(link_element, "attribute", name=column)

    # Add link entity filters (if any)
    if link_entity.link_criteria:
        link_element.append(_filter_to_fetchxml(link_entity.link_criteria))

    # Add nested link-entities (if any)
    if link_entity.link_entities:
        for nested_link in link_entity.link_entities:
            link_element.append(_link_entity_to_fetchxml(nested_link))

    return link_element
