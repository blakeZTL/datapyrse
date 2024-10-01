from datapyrse._entity_metadata import ManyToManyRelationshipMetadata as ManyToManyRelationshipMetadata, ManyToOneRelationshipMetadata as ManyToOneRelationshipMetadata, OneToManyRelationshipMetadata as OneToManyRelationshipMetadata
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._methods import Method as Method
from datapyrse.messages._relate import RelateRequest as RelateRequest
from datapyrse.utils._dataverse import get_entity_collection_name_by_logical_name as get_entity_collection_name_by_logical_name
from logging import Logger
from requests import Request

def get_associate_request(dataverse_request: DataverseRequest, associate_request: RelateRequest, logger: Logger = ...) -> Request: ...
