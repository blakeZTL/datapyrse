from dataclasses import dataclass
from typing import List


@dataclass
class EntityMetadata:
    logical_name: str = None
    attribute_type: str = None
    schema_name: str = None

    def from_json(json: dict) -> "EntityMetadata":
        return EntityMetadata(
            logical_name=json["LogicalName"],
            attribute_type=json["AttributeType"],
            schema_name=json["SchemaName"],
        )


@dataclass
class EntityMetadataResponse:
    value: List[EntityMetadata] = None

    def from_json(json: dict) -> "EntityMetadataResponse":
        return EntityMetadataResponse(
            value=[EntityMetadata.from_json(value) for value in json["value"]],
        )
