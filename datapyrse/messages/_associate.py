"""A module for associating records in Dataverse"""

from logging import Logger, getLogger
from requests import Request

from datapyrse._entity_metadata import (
    ManyToManyRelationshipMetadata,
    ManyToOneRelationshipMetadata,
    OneToManyRelationshipMetadata,
)
from datapyrse.messages._dataverse_request import DataverseRequest
from datapyrse.messages._methods import Method
from datapyrse.utils._dataverse import get_entity_collection_name_by_logical_name
from datapyrse.messages._relate import RelateRequest


def get_associate_request(
    dataverse_request: DataverseRequest,
    associate_request: RelateRequest,
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
