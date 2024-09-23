from dataclasses import dataclass


@dataclass
class OrderExpression:
    attribute_name: str
    order_type: str  # "ASC" or "DESC"
