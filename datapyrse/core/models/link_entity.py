from dataclasses import dataclass, field
from typing import List, Optional
from datapyrse.core.models.column_set import ColumnSet
from datapyrse.core.models.filter_expression import FilterExpression
from enum import Enum


class JoinOperator(Enum):
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
        if not isinstance(self.join_operator, JoinOperator):
            raise ValueError("Join operator must be a JoinOperator")
        if self.columns:
            if not isinstance(self.columns, ColumnSet):
                raise ValueError("Columns must be a ColumnSet")
        if self.link_criteria:
            if not isinstance(self.link_criteria, FilterExpression):
                raise ValueError("Link criteria must be a FilterExpression")
        if self.link_entities:
            if not isinstance(self.link_entities, list):
                raise ValueError("Link entities must be a list")
            for link_entity in self.link_entities:
                if not isinstance(link_entity, LinkEntity):
                    raise ValueError("Link entities must be a list of LinkEntity")
