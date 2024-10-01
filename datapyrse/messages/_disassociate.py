"""A module for disassociating records in Dataverse"""

from logging import Logger, getLogger

from requests import Request

from datapyrse.messages._methods import Method
from datapyrse.messages._dataverse_request import DataverseRequest
from datapyrse.utils._dataverse import get_entity_collection_name_by_logical_name
from datapyrse.messages._relate import RelateRequest


def get_disassociate_request(
    dataverse_request: DataverseRequest,
    disassociate_request: RelateRequest,
    logger: Logger = getLogger(__name__),
) -> list[Request]:
    """
    Get a request to disassociate a primary record with one or more related records

    Args:
        dataverse_request (DataverseRequest): The Dataverse request
        disassociate_request (DisassociateRequest): The disassociate request
        logger (Logger): The logger

    Returns:
        Request: The request
    """
    logger.debug("Getting disassociate request")
    if not dataverse_request:
        msg = "DataverseRequest is required"
        logger.error(msg)
        raise ValueError(msg)
    if not disassociate_request:
        msg = "DisassociateRequest is required"
        logger.error(msg)
        raise ValueError(msg)
    if not disassociate_request.relationship_name:
        msg = "Relationship name is required"
        logger.error(msg)
        raise ValueError(msg)

    related_record_collection_name = get_entity_collection_name_by_logical_name(
        org_metadata=disassociate_request.org_metadata,
        logical_name=disassociate_request.related_records.entity_logical_name,
        logger=logger,
    )
    if not related_record_collection_name:
        msg = "Could not determine related record collection name"
        logger.error(msg)
        raise ValueError(msg)
    requests: list[Request] = []
    if not disassociate_request.relationship_type:
        msg = "Relationship type is required"
        logger.error(msg)
        raise ValueError(msg)

    for related_record in disassociate_request.related_records.entity_references:
        request_url = (
            dataverse_request.endpoint
            + f"/{disassociate_request.relationship_name}"
            + f"({str(related_record.entity_id)})/$ref"
        )
        request: Request = Request(
            method=Method.DELETE.value,
            url=request_url,
            headers=dataverse_request.headers,
        )
        requests.append(request)

    return requests
