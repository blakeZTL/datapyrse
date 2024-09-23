from dataclasses import dataclass, field
from typing import List, Optional
from models.column_set import ColumnSet
from models.filter_expression import FilterExpression


@dataclass
class LinkEntity:
    link_from_entity_name: str
    link_from_attribute_name: str
    link_to_entity_name: str
    link_to_attribute_name: str
    join_operator: str  # Example: "Inner" or "Outer"
    columns: Optional[ColumnSet] = None
    link_criteria: Optional[FilterExpression] = None
    link_entities: Optional[List["LinkEntity"]] = field(default_factory=list)
