"""
A module for creating link entities in queries
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import StrEnum


from datapyrse.query._column_set import ColumnSet
from datapyrse.query._filter_expression import FilterExpression


class JoinOperator(StrEnum):
    """
    Represents a join operator in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of a join operator
    object in Dataverse, including the available join operators.

    Attributes:
        INNER (str): The INNER join operator.
        OUTER (str): The OUTER join operator.
        ANY (str): The ANY join operator.
        NOT_ANY (str): The NOT ANY join operator.
        ALL (str): The ALL join operator.
        NOT_ALL (str): The NOT ALL join operator.
        EXISTS (str): The EXISTS join operator.
        MATCH_FIRST_ROW_USING_CROSS_APPLY (str): The MATCH FIRST ROW USING CROSS APPLY join operator.
    """

    INNER = "inner"
    OUTER = "outer"
    ANY = "any"
    NOT_ANY = "not any"
    ALL = "all"
    NOT_ALL = "not all"
    EXISTS = "exists"
    MATCH_FIRST_ROW_USING_CROSS_APPLY = "matchfirstrowusingcrossapply"


@dataclass
class LinkEntity:
    """
    Represents a link entity in a query.

    This class encapsulates the structure and behavior of a link entity in a query,
    including the entity names, attribute names, join operator, and link criteria.

    Attributes:
        link_from_entity_name (str): The name of the entity to link from.
        link_from_attribute_name (str): The name of the attribute to link from.
        link_to_entity_name (str): The name of the entity to link to.
        link_to_attribute_name (str): The name of the attribute to link to.
        join_operator (JoinOperator): The join operator to use when linking entities.
        columns (Optional[ColumnSet]): The columns to include from the linked entity.
        link_criteria (Optional[FilterExpression]): The criteria to apply to the link.
        link_entities (Optional[List[LinkEntity]]): Additional link entities to include.

    Raises:
        ValueError: If required attributes are not provided.
    """

    link_from_entity_name: str
    link_from_attribute_name: str
    link_to_entity_name: str
    link_to_attribute_name: str
    join_operator: JoinOperator
    columns: Optional[ColumnSet] = None
    link_criteria: Optional[FilterExpression] = None
    link_entities: Optional[List["LinkEntity"]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.link_from_entity_name:
            raise ValueError("Link from entity name is required")
        if not self.link_from_attribute_name:
            raise ValueError("Link from attribute name is required")
        if not self.link_to_entity_name:
            raise ValueError("Link to entity name is required")
        if not self.link_to_attribute_name:
            raise ValueError("Link to attribute name is required")
        if not self.join_operator:
            raise ValueError("Join operator is required")
