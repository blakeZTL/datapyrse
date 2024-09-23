from dataclasses import dataclass, field
from typing import List, Optional
from models.filter_expression import FilterExpression
from models.link_entity import LinkEntity
from models.order_expression import OrderExpression
from models.column_set import ColumnSet


@dataclass
class QueryExpression:
    entity_name: str
    column_set: ColumnSet
    criteria: Optional[FilterExpression] = None
    orders: Optional[List[OrderExpression]] = field(default_factory=list)
    link_entities: Optional[List[LinkEntity]] = field(default_factory=list)
    top_count: Optional[int] = None
    distinct: bool = False
