from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AttributeMetadata:
    logical_name: str | None = None
    attribute_type: str | None = None
    schema_name: str | None = None

    @staticmethod
    def from_json(json: dict) -> "AttributeMetadata":
        return AttributeMetadata(
            logical_name=json["LogicalName"],
            attribute_type=json["AttributeType"],
            schema_name=json["SchemaName"],
        )


@dataclass
class LocalizedLabel:
    has_changed: Optional[bool] | None = None
    is_managed: bool | None = None
    label: str | None = None
    language_code: int | None = None
    metadata_id: str | None = None

    @staticmethod
    def from_json(json: dict) -> "LocalizedLabel":
        return LocalizedLabel(
            has_changed=json.get("HasChanged"),
            is_managed=json["IsManaged"],
            label=json["Label"],
            language_code=json["LanguageCode"],
            metadata_id=json["MetadataId"],
        )


@dataclass
class EntityMetadata:
    attributes: List[AttributeMetadata] | None = None
    logical_name: str | None = None
    logical_collection_name: str | None = None
    schema_name: str | None = None
    primary_id_attribute: str | None = None
    primary_name_attribute: str | None = None

    @staticmethod
    def from_json(json: dict) -> "EntityMetadata":
        return EntityMetadata(
            attributes=[
                AttributeMetadata.from_json(attr) for attr in json["Attributes"]
            ],
            logical_collection_name=json["LogicalCollectionName"],
            logical_name=json["LogicalName"],
            schema_name=json["SchemaName"],
            primary_id_attribute=json["PrimaryIdAttribute"],
            primary_name_attribute=json["PrimaryNameAttribute"],
        )


@dataclass
class OrgMetadata:
    entities: List[EntityMetadata] | None = None

    @staticmethod
    def from_json(json: dict) -> "OrgMetadata":
        return OrgMetadata(
            entities=[EntityMetadata.from_json(entity) for entity in json["value"]]
        )
