"""A module for associating records in Dataverse"""

from dataclasses import dataclass, field
from logging import DEBUG, Logger, getLogger
from typing import Optional, Union

from requests import Request

from datapyrse._entity_reference import EntityReference
from datapyrse._entity_metadata import (
    EntityMetadata,
    ManyToManyRelationshipMetadata,
    ManyToOneRelationshipMetadata,
    OrgMetadata,
    OneToManyRelationshipMetadata,
)
from datapyrse.messages._dataverse_request import DataverseRequest
from datapyrse.messages._methods import Method
from datapyrse.utils._dataverse import get_entity_collection_name_by_logical_name
from datapyrse._entity_reference_collection import EntityReferenceCollection


@dataclass
class AssociateRequest:
    """
    Represents a request to associate a primary record with one or more related records

    Attributes:
        primary_record: EntityReference
            The primary record to associate with related records
        related_records: list[EntityReference]
            The related records to associate with the primary record that
            all have the same entity_logical_name
        org_metadata: OrgMetadata
            The organization metadata
        relationship_name: Optional[str] = None
            The name of the relationship to use for the association
    """

    primary_record: EntityReference
    related_records: EntityReferenceCollection
    org_metadata: OrgMetadata
    relationship_name: Optional[str] = None
    relationship_type: Optional[
        Union[
            OneToManyRelationshipMetadata,
            ManyToManyRelationshipMetadata,
            ManyToOneRelationshipMetadata,
        ]
    ] = field(init=False)
    logger: Logger = field(default_factory=lambda: getLogger(__name__))

    def __post_init__(self) -> None:
        if not self.primary_record:
            raise ValueError("Primary record is required")
        if not self.related_records:
            raise ValueError("Related records are required")
        if not self.org_metadata:
            raise ValueError("Organization metadata is required")

    def validate_relationship_name(
        self,
        logger: Optional[Logger] = None,
    ) -> Optional[
        Union[
            OneToManyRelationshipMetadata,
            ManyToOneRelationshipMetadata,
            ManyToManyRelationshipMetadata,
        ]
    ]:
        if not logger:
            logger = self.logger
        logger.setLevel(DEBUG)
        logger.debug("Validating relationship name")
        if not self.relationship_name:
            raise ValueError("Relationship name is required")
        if (
            not self.org_metadata.entities
            or not self.org_metadata.contains_relationships
        ):
            raise ValueError(
                "No entities or relationships found in organization metadata"
            )

        entity_metadata: EntityMetadata | None = next(
            (
                entity
                for entity in self.org_metadata.entities
                if entity.logical_name == self.primary_record.entity_logical_name
                or entity.logical_name
                in [
                    entity.entity_logical_name
                    for entity in self.related_records.entity_references
                ]
            ),
            None,
        )
        if not entity_metadata:
            raise ValueError(
                f"Entity metadata not found for {self.primary_record.entity_logical_name}"
            )
        if entity_metadata.one_to_many_relationships:
            logger.debug(
                "One to Many Relationships: %s",
                entity_metadata.one_to_many_relationships,
            )
            one_to_many_relationships: list[OneToManyRelationshipMetadata] = [
                relationship
                for relationship in entity_metadata.one_to_many_relationships
                if relationship.referenced_entity
                == self.primary_record.entity_logical_name
                and relationship.referencing_entity
                == self.related_records.entity_references[0].entity_logical_name
                and relationship.schema_name.lower() == self.relationship_name.lower()
            ]
            if one_to_many_relationships and len(one_to_many_relationships) == 1:
                logger.debug("One to Many Relationship: %s", one_to_many_relationships)
                return one_to_many_relationships[0]
            if len(one_to_many_relationships) > 1:
                logger.warning("Multiple one to many relationships found")
                for relationship in one_to_many_relationships:
                    logger.warning(
                        "One to Many Relationship: %s", relationship.schema_name
                    )
        else:
            logger.debug(
                f"No one to many relationships found for {self.primary_record.entity_logical_name}"
            )
        if entity_metadata.many_to_one_relationships:
            logger.debug(
                "Many to One Relationships: %s",
                entity_metadata.many_to_one_relationships,
            )
            many_to_one_relationships: list[ManyToOneRelationshipMetadata] = [
                relationship
                for relationship in entity_metadata.many_to_one_relationships
                if relationship.referenced_entity
                == self.primary_record.entity_logical_name
                and relationship.referencing_entity
                == self.related_records.entity_references[0].entity_logical_name
                and relationship.schema_name.lower() == self.relationship_name.lower()
            ]
            if many_to_one_relationships and len(many_to_one_relationships) == 1:
                logger.debug("Many to One Relationship: %s", many_to_one_relationships)
                logger.debug(
                    "referenced: %s\nreferencing: %s\nprimary: %s\nrelated: %s",
                    many_to_one_relationships[0].referenced_entity,
                    many_to_one_relationships[0].referencing_entity,
                    self.primary_record.entity_logical_name,
                    self.related_records.entity_references[0].entity_logical_name,
                )
                return many_to_one_relationships[0]
            if len(many_to_one_relationships) > 1:
                logger.warning("Multiple many to one relationships found")
                for relationship in many_to_one_relationships:
                    logger.warning(
                        "Many to One Relationship: %s", relationship.schema_name
                    )
        else:
            logger.debug(
                f"No many to one relationships found for {self.primary_record.entity_logical_name}"
            )
        if entity_metadata.many_to_many_relationships:
            logger.debug(
                "Many to Many Relationships: %s",
                entity_metadata.many_to_many_relationships,
            )
            many_to_many_relationships: list[ManyToManyRelationshipMetadata] = [
                relationship
                for relationship in entity_metadata.many_to_many_relationships
                if relationship.entity_1_logical_name
                == self.primary_record.entity_logical_name
                and relationship.entity_2_logical_name
                == self.related_records.entity_references[0].entity_logical_name
                and relationship.schema_name.lower() == self.relationship_name.lower()
            ]
            if many_to_many_relationships and len(many_to_many_relationships) == 1:
                logger.debug(
                    "Many to Many Relationship: %s", many_to_many_relationships
                )
                return many_to_many_relationships[0]
            if len(many_to_many_relationships) > 1:
                logger.warning("Multiple many to many relationships found")
                for relationship in many_to_many_relationships:
                    logger.warning(
                        "Many to Many Relationship: %s", relationship.schema_name
                    )
        else:
            logger.debug(
                f"No many to many relationships found for {self.primary_record.entity_logical_name}"
            )

        logger.error(
            f"Relationship name {self.relationship_name} not found in metadata"
        )
        return None

    def parse_relationship_name(
        self,
    ) -> tuple[
        Optional[str],
        Optional[
            Union[
                OneToManyRelationshipMetadata,
                ManyToManyRelationshipMetadata,
                ManyToOneRelationshipMetadata,
            ]
        ],
    ]:
        self.logger.debug("Parsing relationship name")
        if not self.org_metadata.entities:
            raise ValueError("No entities found in organization metadata")

        entity_metadata: EntityMetadata | None = next(
            (
                entity
                for entity in self.org_metadata.entities
                if entity.logical_name == self.primary_record.entity_logical_name
            ),
            None,
        )
        if not entity_metadata:
            return None, None
        possible_one_to_many: list[OneToManyRelationshipMetadata] = []
        if entity_metadata.one_to_many_relationships:
            self.logger.debug(
                "checking one to many relationships: %s",
                entity_metadata.one_to_many_relationships,
            )
            for relationship in entity_metadata.one_to_many_relationships:
                if (
                    relationship.referenced_entity
                    == self.primary_record.entity_logical_name
                    and relationship.referencing_entity
                    == self.related_records.entity_references[0].entity_logical_name
                ):
                    self.logger.debug(
                        "Relationship: %s, %s, %s, %s",
                        relationship.referenced_entity,
                        self.primary_record.entity_logical_name,
                        relationship.referencing_entity,
                        self.related_records.entity_references[0].entity_logical_name,
                    )
                    possible_one_to_many.append(relationship)
        if len(possible_one_to_many) > 1:
            return None, None
        possible_many_to_one: list[ManyToOneRelationshipMetadata] = []
        if entity_metadata.many_to_one_relationships:
            self.logger.debug(
                "checking many to one relationships: %s",
                entity_metadata.many_to_one_relationships,
            )
            for relationship in entity_metadata.many_to_one_relationships:
                if (
                    relationship.referenced_entity
                    == self.primary_record.entity_logical_name
                    and relationship.referencing_entity
                    == self.related_records.entity_references[0].entity_logical_name
                ):
                    self.logger.debug(
                        "Relationship: %s, %s, %s, %s",
                        relationship.referenced_entity,
                        self.primary_record.entity_logical_name,
                        relationship.referencing_entity,
                        self.related_records.entity_references[0].entity_logical_name,
                    )
                    possible_many_to_one.append(relationship)
        if len(possible_many_to_one) > 1:
            return None, None
        possible_many_to_many: list[ManyToManyRelationshipMetadata] = []
        if entity_metadata.many_to_many_relationships:
            self.logger.debug(
                "checking many to many relationships: %s",
                entity_metadata.many_to_many_relationships,
            )
            for relationship in entity_metadata.many_to_many_relationships:
                if (
                    relationship.entity_1_logical_name
                    == self.primary_record.entity_logical_name
                    and relationship.entity_2_logical_name
                    == self.related_records.entity_references[0].entity_logical_name
                ):
                    self.logger.debug(
                        "Relationship: %s, %s, %s, %s",
                        relationship.entity_1_logical_name,
                        self.primary_record.entity_logical_name,
                        relationship.entity_2_logical_name,
                        self.related_records.entity_references[0].entity_logical_name,
                    )
                    possible_many_to_many.append(relationship)
        if len(possible_many_to_many) > 1:
            return None, None
        if (
            possible_one_to_many
            and not possible_many_to_one
            and not possible_many_to_many
        ):
            self.logger.debug(
                "One to Many Relationship: %s", possible_one_to_many[0].schema_name
            )
            return possible_one_to_many[0].schema_name, possible_one_to_many[0]
        if (
            possible_many_to_one
            and not possible_one_to_many
            and not possible_many_to_many
        ):
            self.logger.debug(
                "Many to One Relationship: %s", possible_many_to_one[0].schema_name
            )
            return possible_many_to_one[0].schema_name, possible_many_to_one[0]
        if (
            possible_many_to_many
            and not possible_one_to_many
            and not possible_many_to_one
        ):
            self.logger.debug(
                "Many to Many Relationship: %s", possible_many_to_many[0].schema_name
            )
            return possible_many_to_many[0].schema_name, possible_many_to_many[0]
        self.logger.warning(
            f"Relationship name {self.relationship_name} not found in metadata"
        )
        return None, None


def get_associate_request(
    dataverse_request: DataverseRequest,
    associate_request: AssociateRequest,
    logger: Logger = getLogger(__name__),
) -> Request:
    """
    Get a request to associate a primary record with one or more related records

    Args:
        dataverse_request (DataverseRequest): The Dataverse request
        associate_request (AssociateRequest): The associate request
        logger (Logger): The logger

    Returns:
        Request: The request
    """
    logger.debug("Getting associate request")
    if not dataverse_request:
        msg = "DataverseRequest is required"
        logger.error(msg)
        raise ValueError(msg)
    if not associate_request:
        msg = "AssociateRequest is required"
        logger.error(msg)
        raise ValueError(msg)
    if not associate_request.relationship_name:
        msg = "Relationship name is required"
        logger.error(msg)
        raise ValueError(msg)

    json_data: dict[str, str] = {}
    related_record_collection_name = get_entity_collection_name_by_logical_name(
        org_metadata=associate_request.org_metadata,
        logical_name=associate_request.related_records.entity_references[
            0
        ].entity_logical_name,
        logger=logger,
    )
    if not related_record_collection_name:
        msg = "Could not determine related record collection name"
        logger.error(msg)
        raise ValueError(msg)

    if associate_request.relationship_type and (
        isinstance(
            associate_request.relationship_type,
            (ManyToManyRelationshipMetadata, ManyToOneRelationshipMetadata),
        )
    ):
        if isinstance(
            associate_request.relationship_type, ManyToOneRelationshipMetadata
        ):
            if (
                associate_request.primary_record.entity_logical_name
                != associate_request.relationship_type.referenced_entity
            ):
                msg = "Primary record must be the referenced entity for a many-to-one relationship"
                logger.error(msg)
                raise ValueError(msg)
        for related_record in associate_request.related_records.entity_references:
            json_data["@odata.id"] = (
                dataverse_request.base_url
                + "/api/data/v9.2/"
                + related_record_collection_name
                + f"({str(related_record.entity_id)})"
            )
    else:
        if len(associate_request.related_records.entity_references) > 1:
            msg = "Cannot associate multiple records with a one-to-many relationship"
            logger.error(msg)
            raise ValueError(msg)
        if (
            isinstance(
                associate_request.relationship_type, OneToManyRelationshipMetadata
            )
            and associate_request.primary_record.entity_logical_name
            != associate_request.relationship_type.referenced_entity
        ):
            msg = "Primary record must be the referenced entity for a one-to-many relationship"
            logger.error(msg)
            raise ValueError(msg)
        json_data["@odata.id"] = (
            dataverse_request.base_url
            + "/api/data/v9.2/"
            + related_record_collection_name
            + f"({str(associate_request.related_records.entity_references[0].entity_id)})"
        )
    logger.debug("Related record: %s", json_data)
    url = (
        dataverse_request.endpoint.split("?")[0]
        + f"/{associate_request.relationship_name}/$ref"
    )
    if dataverse_request.tag:
        url += f"?tag={dataverse_request.tag}"
    request: Request = Request(
        method=Method.POST.value,
        url=url,
        headers=dataverse_request.headers,
        json=json_data,
    )
    return request
