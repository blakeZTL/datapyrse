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

    def __post_init__(self) -> None:
        if not self.entity_name:
            raise Exception("Entity name is required")

        if not isinstance(self.entity_name, str):
            raise Exception("Entity name must be a string")

        if not self.column_set:
            raise Exception("Column set is required")

        if not isinstance(self.column_set, ColumnSet):
            raise Exception("Column set must be a ColumnSet")

        if self.criteria:
            if not isinstance(self.criteria, FilterExpression):
                raise Exception("Criteria must be a FilterExpression")

        if self.orders:
            if not isinstance(self.orders, list):
                raise Exception("Orders must be a list of OrderExpressions")

        if self.link_entities:
            if not isinstance(self.link_entities, list):
                raise Exception("Link entities must be a list of LinkEntities")

        if self.top_count is not None:
            if not isinstance(self.top_count, int):
                raise Exception("Top count must be an integer")
            if self.top_count < 1:
                raise Exception("Top count must be greater than 0")

        if not isinstance(self.distinct, bool):
            raise Exception("Distinct must be a boolean")

    def to_fetchxml(self) -> str:
        from utils.query_to_fetch import query_expression_to_fetchxml

        return query_expression_to_fetchxml(self)
