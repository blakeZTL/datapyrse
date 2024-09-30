from dataclasses import dataclass
from datapyrse.query._column_set import ColumnSet as ColumnSet
from datapyrse.query._filter_expression import FilterExpression as FilterExpression
from enum import StrEnum

class JoinOperator(StrEnum):
    INNER = 'inner'
    OUTER = 'outer'
    ANY = 'any'
    NOT_ANY = 'not any'
    ALL = 'all'
    NOT_ALL = 'not all'
    EXISTS = 'exists'
    MATCH_FIRST_ROW_USING_CROSS_APPLY = 'matchfirstrowusingcrossapply'

@dataclass
class LinkEntity:
    link_from_entity_name: str
    link_from_attribute_name: str
    link_to_entity_name: str
    link_to_attribute_name: str
    join_operator: JoinOperator
    columns: ColumnSet | None = ...
    link_criteria: FilterExpression | None = ...
    link_entities: list['LinkEntity'] | None = ...
    def __post_init__(self) -> None: ...
    def __init__(self, link_from_entity_name, link_from_attribute_name, link_to_entity_name, link_to_attribute_name, join_operator, columns=..., link_criteria=..., link_entities=...) -> None: ...
