"""
A module for entity metadata in Dataverse
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ManyToManyRelationshipMetadata:
    """
    Represents a many-to-many relationship in Dataverse.

    This class encapsulates the core structure and behavior of a many-to-many
    relationship in Dataverse, including the intersect attribute, intersect entity,
    entity 1 intersect attribute, entity 1 logical name, entity 1 navigation property name,
    entity 2 intersect attribute, entity 2 logical name, entity 2 navigation property name,
    schema name, and intersect entity name.

    Attributes:
        intersect_attribute (str): The intersect attribute in the relationship.
        intersect_entity (str): The intersect entity in the relationship.
        entity_1_intersect_attribute (str): The intersect attribute of entity 1.
        entity_1_logical_name (str): The logical name of entity 1.
        entity_1_navigation_property_name (str): The navigation property name of entity 1.
        entity_2_intersect_attribute (str): The intersect attribute of entity 2.
        entity_2_logical_name (str): The logical name of entity 2.
        entity_2_navigation_property_name (str): The navigation property name of entity 2.
        schema_name (str): The schema name of the relationship.
        intersect_entity_name (str): The name of the intersect entity.

    Methods:
        from_json(json: dict[str, Any]) -> ManyToManyRelationship: Create a
            ManyToManyRelationship instance from a JSON object.
    """

    entity_1_intersect_attribute: str
    entity_1_logical_name: str
    entity_1_navigation_property_name: str
    entity_2_intersect_attribute: str
    entity_2_logical_name: str
    entity_2_navigation_property_name: str
    schema_name: str
    intersect_entity_name: str

    @staticmethod
    def from_json(json: dict[str, Any]) -> "ManyToManyRelationshipMetadata":
        """
        Create a ManyToManyRelationship instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing a many-to-many relationship.

        Returns:
            ManyToManyRelationship: A ManyToManyRelationship instance created from the JSON object.
        """
        return ManyToManyRelationshipMetadata(
            entity_1_intersect_attribute=json["Entity1IntersectAttribute"],
            entity_1_logical_name=json["Entity1LogicalName"],
            entity_1_navigation_property_name=json["Entity1NavigationPropertyName"],
            entity_2_intersect_attribute=json["Entity2IntersectAttribute"],
            entity_2_logical_name=json["Entity2LogicalName"],
            entity_2_navigation_property_name=json["Entity2NavigationPropertyName"],
            schema_name=json["SchemaName"],
            intersect_entity_name=json["IntersectEntityName"],
        )


@dataclass
class ManyToOneRelationshipMetadata:
    """
    Represents a many-to-one relationship in Dataverse.

    This class encapsulates the core structure and behavior of a many-to-one
    relationship in Dataverse, including the referenced attribute, referenced
    entity, referenced entity navigation property name, referencing attribute,
    referencing entity, referencing entity navigation property name, and schema name.

    Attributes:
        referenced_attribute (str): The referenced attribute in the relationship.
        referenced_entity (str): The referenced entity in the relationship.
        referenced_entity_navigation_property_name (str): The navigation property name
            of the referenced entity.
        referencing_attribute (str): The referencing attribute in the relationship.
        referencing_entity (str): The referencing entity in the relationship.
        referencing_entity_navigation_property_name (str): The navigation property name
            of the referencing entity.
        schema_name (str): The schema name of the relationship.

    Methods:
        from_json(json: dict[str, Any]) -> ManyToOneRelationship: Create a
            ManyToOneRelationship instance from a JSON object.
    """

    referenced_attribute: str
    referenced_entity: str
    referenced_entity_navigation_property_name: str
    referencing_attribute: str
    referencing_entity: str
    referencing_entity_navigation_property_name: str
    schema_name: str

    @staticmethod
    def from_json(json: dict[str, Any]) -> "ManyToOneRelationshipMetadata":
        """
        Create a ManyToOneRelationship instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing a many-to-one relationship.

        Returns:
            ManyToOneRelationship: A ManyToOneRelationship instance created from the JSON object.
        """
        return ManyToOneRelationshipMetadata(
            referenced_attribute=json["ReferencedAttribute"],
            referenced_entity=json["ReferencedEntity"],
            referenced_entity_navigation_property_name=json[
                "ReferencedEntityNavigationPropertyName"
            ],
            referencing_attribute=json["ReferencingAttribute"],
            referencing_entity=json["ReferencingEntity"],
            referencing_entity_navigation_property_name=json[
                "ReferencingEntityNavigationPropertyName"
            ],
            schema_name=json["SchemaName"],
        )


@dataclass
class OneToManyRelationshipMetadata:
    """
    Represents a one-to-many relationship in Dataverse.

    This class encapsulates the core structure and behavior of a one-to-many
    relationship in Dataverse, including the referenced attribute, referenced
    entity, referenced entity navigation property name, referencing attribute,
    referencing entity, referencing entity navigation property name, and schema name.

    Attributes:
        referenced_attribute (str): The referenced attribute in the relationship.
        referenced_entity (str): The referenced entity in the relationship.
        referenced_entity_navigation_property_name (str): The navigation property name
            of the referenced entity.
        referencing_attribute (str): The referencing attribute in the relationship.
        referencing_entity (str): The referencing entity in the relationship.
        referencing_entity_navigation_property_name (str): The navigation property name
            of the referencing entity.
        schema_name (str): The schema name of the relationship.

    Methods:
        from_json(json: dict[str, Any]) -> OneToManyRelationship: Create a
            OneToManyRelationship instance from a JSON object.
    """

    referenced_attribute: str
    referenced_entity: str
    referenced_entity_navigation_property_name: str
    referencing_attribute: str
    referencing_entity: str
    referencing_entity_navigation_property_name: str
    schema_name: str

    @staticmethod
    def from_json(json: dict[str, Any]) -> "OneToManyRelationshipMetadata":
        """
        Create a OneToManyRelationship instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing a one-to-many relationship.

        Returns:
            OneToManyRelationship: A OneToManyRelationship instance created from the JSON object.
        """
        return OneToManyRelationshipMetadata(
            referenced_attribute=json["ReferencedAttribute"],
            referenced_entity=json["ReferencedEntity"],
            referenced_entity_navigation_property_name=json[
                "ReferencedEntityNavigationPropertyName"
            ],
            referencing_attribute=json["ReferencingAttribute"],
            referencing_entity=json["ReferencingEntity"],
            referencing_entity_navigation_property_name=json[
                "ReferencingEntityNavigationPropertyName"
            ],
            schema_name=json["SchemaName"],
        )


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
    one_to_many_relationships: List[OneToManyRelationshipMetadata] | None = None
    many_to_one_relationships: List[ManyToOneRelationshipMetadata] | None = None
    many_to_many_relationships: List[ManyToManyRelationshipMetadata] | None = None

    @staticmethod
    def from_json(json: dict[str, Any]) -> "EntityMetadata":
        """
        Create an EntityMetadata instance from a JSON object.

        Args:
            json (dict[str, Any]): A JSON object representing an entity metadata.

        Returns:
            EntityMetadata: An EntityMetadata instance created from the JSON object.
        """
        entity_metadata: EntityMetadata = EntityMetadata(
            attributes=[
                AttributeMetadata.from_json(attr) for attr in json["Attributes"]
            ],
            logical_collection_name=json["LogicalCollectionName"],
            logical_name=json["LogicalName"],
            schema_name=json["SchemaName"],
            primary_id_attribute=json["PrimaryIdAttribute"],
            primary_name_attribute=json["PrimaryNameAttribute"],
        )
        if "OneToManyRelationships" in json:
            entity_metadata.one_to_many_relationships = [
                OneToManyRelationshipMetadata.from_json(rel)
                for rel in json["OneToManyRelationships"]
            ]
        if "ManyToOneRelationships" in json:
            entity_metadata.many_to_one_relationships = [
                ManyToOneRelationshipMetadata.from_json(rel)
                for rel in json["ManyToOneRelationships"]
            ]
        if "ManyToManyRelationships" in json:
            entity_metadata.many_to_many_relationships = [
                ManyToManyRelationshipMetadata.from_json(rel)
                for rel in json["ManyToManyRelationships"]
            ]

        return entity_metadata


@dataclass
class OrgMetadata:
    """
    Represents organization metadata in Dataverse.

    This class encapsulates the core structure and behavior of organization metadata
    in Dataverse, including a list of entity metadata objects.

    Attributes:
        entities (List[EntityMetadata]): A list of entity metadata objects.
        contains_relationships (bool): Whether the organization's entity metadata contains relationships

    Methods:
        from_json(json: dict[str, Any]) -> OrgMetadata: Create an OrgMetadata instance
            from a JSON object.
    """

    entities: List[EntityMetadata] | None = None
    contains_relationships: bool = False

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
