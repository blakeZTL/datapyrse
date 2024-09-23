import xml.etree.ElementTree as ET
from typing import List, Optional
from models.query_expression import QueryExpression
from models.filter_expression import FilterExpression
from models.link_entity import LinkEntity


# TODO: Implement unit testing for this function
def query_expression_to_fetchxml(query: QueryExpression) -> str:
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
    if query.column_set.all_columns:
        ET.SubElement(entity, "all-attributes")
    else:
        for column in query.column_set.columns:
            ET.SubElement(entity, "attribute", name=column)

    # Add filters (if any)
    if query.criteria:
        entity.append(filter_to_fetchxml(query.criteria))

    # Add orders (if any)
    for order in query.orders:
        ET.SubElement(
            entity,
            "order",
            attribute=order.attribute_name,
            descending=("true" if order.order_type == "DESC" else "false"),
        )

    # Add linked entities (if any)
    for link_entity in query.link_entities:
        entity.append(link_entity_to_fetchxml(link_entity))

    # Convert the XML tree to a string
    return ET.tostring(fetch, encoding="unicode")


# TODO: Implement unit testing for this function
def filter_to_fetchxml(filter_expression: FilterExpression) -> ET.Element:
    filter_element = ET.Element(
        "filter", type=filter_expression.filter_operator.lower()
    )

    # Add conditions
    for condition in filter_expression.conditions:
        condition_element = ET.SubElement(
            filter_element,
            "condition",
            attribute=condition.attribute_name,
            operator=condition.operator.lower(),
        )
        if condition.values:
            for value in condition.values:
                value_element = ET.SubElement(condition_element, "value")
                value_element.text = str(value)

    # Add nested filters (if any)
    for sub_filter in filter_expression.filters:
        filter_element.append(filter_to_fetchxml(sub_filter))

    return filter_element


# TODO: Implement unit testing for this function
def link_entity_to_fetchxml(link_entity: LinkEntity) -> ET.Element:
    link_element = ET.Element(
        "link-entity",
        name=link_entity.link_to_entity_name,
        from_=link_entity.link_from_attribute_name,
        to=link_entity.link_to_attribute_name,
        linktype=link_entity.join_operator.lower(),
    )

    # Add linked entity columns (if any)
    if link_entity.columns:
        if link_entity.columns.all_columns:
            ET.SubElement(link_element, "all-attributes")
        else:
            for column in link_entity.columns.columns:
                ET.SubElement(link_element, "attribute", name=column)

    # Add link entity filters (if any)
    if link_entity.link_criteria:
        link_element.append(filter_to_fetchxml(link_entity.link_criteria))

    # Add nested link-entities (if any)
    for nested_link in link_entity.link_entities:
        link_element.append(link_entity_to_fetchxml(nested_link))

    return link_element
