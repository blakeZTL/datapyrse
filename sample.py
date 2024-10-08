from uuid import UUID
import sys
from datapyrse import (
    ServiceClient,
    Entity,
    EntityCollection,
    EntityReference,
    EntityReferenceCollection,
)
from datapyrse.query import QueryExpression, ColumnSet
from datapyrse.messages import (
    RetrieveMultipleResponse,
    RetrieveResponse,
    CreateResponse,
    DeleteResponse,
)


service: ServiceClient = ServiceClient(
    tenant_id="YOUR_TENANT_ID",
    resource_url="YOUR_RESOURCE_URL",  # e.g. https://yourorg.crm.dynamics.com
)
if not service.is_ready:
    print("Service not ready")
    sys.exit(1)


# Retrieve multiple entities
query: QueryExpression = QueryExpression(
    "new_tablename", ColumnSet(["new_name", "ownerid"])
)
rm_response: RetrieveMultipleResponse = service.retrieve_multiple(query)
entities: EntityCollection = rm_response.entities

if entities.entities:
    for ent in entities.entities:
        print(f"\nId: {ent.entity_id}")
        for attribute in ent.attributes:
            print(f"  {attribute}: {ent.attributes[attribute]}")
        print()

# Retrieve a single entity
r_response: RetrieveResponse = service.retrieve(
    "new_tablename", UUID("YOUR_GUID"), ColumnSet(["new_name", "ownerid"])
)
entity: Entity = r_response.entity

# Create a new entity
new_entity: Entity = Entity("new_tablename")
new_entity["new_name"] = "New Entity"

user_id: UUID = UUID("USER_GUID")
new_entity["ownerid"] = EntityReference("systemuser", user_id)

c_response: CreateResponse = service.create(new_entity)
if c_response.entity.entity_id:
    new_entity_id: UUID = c_response.entity.entity_id

# Delete an entity
d_response: DeleteResponse = service.delete(
    entity_logical_name="new_tablename", entity_id=UUID("YOUR GUID")
)
if d_response.was_deleted is True:
    print("Entity deleted")

# Associate
service.associate(
    target=EntityReference(
        entity_logical_name="new_tablename", entity_id=UUID("A_GUID")
    ),
    related_entities=EntityReferenceCollection(
        entity_logical_name="new_anothertablename",
        entity_references=[
            EntityReference(
                entity_logical_name="new_anothertablename",
                entity_id=UUID("ANOTHER_GUID"),
            ),
        ],
    ),
    relationship_name="the_relationship_Schema_Name",
)

# Disassociate
service.disassociate(
    target=EntityReference(
        entity_logical_name="new_tablename", entity_id=UUID("A_GUID")
    ),
    related_entities=EntityReferenceCollection(
        entity_logical_name="new_anothertablename",
        entity_references=[
            EntityReference(
                entity_logical_name="new_anothertablename",
                entity_id=UUID("ANOTHER_GUID"),
            ),
        ],
    ),
    relationship_name="the_relationship_Schema_Name",
)
