# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, unused-argument

from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import StrEnum

from datapyrse.models.column_set import ColumnSet
from datapyrse.models.condition_expression import ConditionExpression

class FilterOperator(StrEnum):
    AND = "AND"
    OR = "OR"

@dataclass
class FilterExpression:
    filter_operator: FilterOperator = field(default=FilterOperator.AND)
    conditions: List[ConditionExpression] = field(default_factory=list)
    filters: List["FilterExpression"] = field(default_factory=list)

    def __post_init__(self) -> None: ...

class JoinOperator(StrEnum):
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

    def __post_init__(self) -> None: ...

@dataclass
class OptionSet:
    label: Optional[str] = field(default=None)
    value: Optional[int] = field(default=None)

    def to_dict(self) -> dict[str, Optional[Union[str, int]]]: ...
    def get_option_value(self) -> int | None: ...
    def get_option_label(self) -> str | None: ...

class OrderType(StrEnum):
    ASC = "ASC"
    DESC = "DESC"

@dataclass
class OrderExpression:
    column_name: str
    order_type: OrderType = OrderType.ASC

    def __post_init__(self) -> None: ...

@dataclass
class QueryExpression:
    entity_name: str
    column_set: ColumnSet
    criteria: Optional[FilterExpression] = None
    orders: Optional[List[OrderExpression]] = field(default_factory=list)
    link_entities: Optional[List[LinkEntity]] = field(default_factory=list)
    top_count: Optional[int] = None
    distinct: bool = False

    def __post_init__(self) -> None: ...
    def to_dict(
        self,
    ) -> dict[
        str,
        Union[
            str,
            ColumnSet,
            Optional[FilterExpression],
            List[OrderExpression],
            List[LinkEntity],
            Optional[int],
            bool,
        ],
    ]: ...
    def to_fetchxml(self) -> str: ...

def _query_expression_to_fetchxml(query: QueryExpression) -> str: ...
def _filter_expression_to_fetchxml(filter_expression: FilterExpression) -> str: ...
def _link_entity_to_fetchxml(link_entity: LinkEntity) -> str: ...
