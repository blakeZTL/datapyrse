"""
A module for entity metadata in Dataverse
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class AttributeMetadata:
    """
    Represents an attribute metadata object in Dataverse.

    This class encapsulates the core structure and behavior of an attribute
    metadata object in Dataverse, including the logical name, attribute type,
    and schema name.

    Attributes:
        logical_name (str): The logical name of the attribute in Dataverse.
        attribute_type (str): The type of the attribute in Dataverse.
        schema_name (str): The schema name of the attribute in Dataverse.

    Methods:
        from_json(json: dict[str, Any]) -> AttributeMetadata: Create an
            AttributeMetadata instance from a JSON object.
    """

    logical_name: str | None = None
    attribute_type: str | None = None
    schema_name: str | None = None

    @staticmethod
    def from_json(json: dict[str, Any]) -> "AttributeMetadata":
        """
        Create an AttributeMetadata instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing an attribute metadata.

        Returns:
            AttributeMetadata: An AttributeMetadata instance created from the JSON object.
        """
        return AttributeMetadata(
            logical_name=json["LogicalName"],
            attribute_type=json["AttributeType"],
            schema_name=json["SchemaName"],
        )


@dataclass
class LocalizedLabel:
    """
    Represents a localized label object in Dataverse.

    This class encapsulates the core structure and behavior of a localized label
    object in Dataverse, including the label text, language code, and metadata ID.

    Attributes:
        has_changed (Optional[bool]): Whether the label has changed.
        is_managed (bool): Whether the label is managed.
        label (str): The text of the label.
        language_code (int): The language code of the label.
        metadata_id (str): The metadata ID of the label.

    Methods:

        from_json(json: dict[str, Any]) -> LocalizedLabel: Create a LocalizedLabel
            instance from a JSON object.
    """

    has_changed: Optional[bool] | None = None
    is_managed: bool | None = None
    label: str | None = None
    language_code: int | None = None
    metadata_id: str | None = None

    @staticmethod
    def from_json(json: dict[str, Any]) -> "LocalizedLabel":
        """
        Create a LocalizedLabel instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing a localized label.

        Returns:
            LocalizedLabel: A LocalizedLabel instance created from the JSON object.
        """
        return LocalizedLabel(
            has_changed=json.get("HasChanged"),
            is_managed=json["IsManaged"],
            label=json["Label"],
            language_code=json["LanguageCode"],
            metadata_id=json["MetadataId"],
        )


@dataclass
class EntityMetadata:
    """
    Represents an entity metadata object in Dataverse.

    This class encapsulates the core structure and behavior of an entity metadata
    object in Dataverse, including the attributes, logical name, collection name,
    schema name, primary ID attribute, and primary name attribute.

    Attributes:
        attributes (List[AttributeMetadata]): A list of attribute metadata objects.
        logical_name (str): The logical name of the entity in Dataverse.
        logical_collection_name (str): The logical collection name of the entity.
        schema_name (str): The schema name of the entity in Dataverse.
        primary_id_attribute (str): The primary ID attribute of the entity.
        primary_name_attribute (str): The primary name attribute of the entity.

    Methods:
        from_json(json: dict[str, Any]) -> EntityMetadata: Create an EntityMetadata
            instance from a JSON object.
    """

    attributes: List[AttributeMetadata] | None = None
    logical_name: str | None = None
    logical_collection_name: str | None = None
    schema_name: str | None = None
    primary_id_attribute: str | None = None
    primary_name_attribute: str | None = None

    @staticmethod
    def from_json(json: dict[str, Any]) -> "EntityMetadata":
        """
        Create an EntityMetadata instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing an entity metadata.

        Returns:
            EntityMetadata: An EntityMetadata instance created from the JSON object.
        """
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
    """
    Represents organization metadata in Dataverse.

    This class encapsulates the core structure and behavior of organization metadata
    in Dataverse, including a list of entity metadata objects.

    Attributes:
        entities (List[EntityMetadata]): A list of entity metadata objects.

    Methods:
        from_json(json: dict[str, Any]) -> OrgMetadata: Create an OrgMetadata instance
            from a JSON object.
    """

    entities: List[EntityMetadata] | None = None

    @staticmethod
    def from_json(json: dict[str, Any]) -> "OrgMetadata":
        """
        Create an OrgMetadata instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing organization metadata.

        Returns:
            OrgMetadata: An OrgMetadata instance created from the JSON object.
        """
        return OrgMetadata(
            entities=[EntityMetadata.from_json(entity) for entity in json["value"]]
        )
