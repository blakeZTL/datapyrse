from uuid import UUID
from datapyrse.core import *
from datapyrse.core.query import *


service: ServiceClient = ServiceClient(
    tenant_id="YOUR_TENANT_ID",
    resource_url="YOUR_RESOURCE_URL",  # e.g. https://yourorg.crm.dynamics.com
)
if not service.IsReady:
    print("Service not ready")
    exit(1)


# Retrieve multiple entities
query: QueryExpression = QueryExpression(
    "new_tablename", ColumnSet(["new_name", "ownerid"])
)
entities: EntityCollection = service.retrieve_multiple(query)

if entities.entities:
    for ent in entities.entities:
        print(f"\nId: {ent.entity_id}")
        for attribute in ent.attributes:
            print(f"  {attribute}: {ent.attributes[attribute]}")
        print()

# Retrieve a single entity
entity: Entity = service.retrieve(
    "new_tablename", UUID("YOUR_GUID"), ColumnSet(["new_name", "ownerid"])
)

# Create a new entity
new_entity: Entity = Entity("new_tablename")
new_entity["new_name"] = "New Entity"

user_id: UUID = UUID("USER_GUID")
new_entity["ownerid"] = EntityReference("systemuser", user_id)

service.create(new_entity)

# Delete an entity
service.delete(entity_name="new_tablename", entity_id=UUID("YOUR GUID"))
service.delete(entity_name="new_tablename", entity_id="YOUR GUID AS STRING")
service.delete(entity=Entity("new_tablename", UUID("YOUR GUID")))
service.delete(entity_reference=EntityReference("new_tablename", UUID("YOUR GUID")))
