import uuid
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

for ent in entities.entities:
    print(f"\nId: {ent.entity_id}")
    for attribute in ent.attributes:
        print(f"  {attribute}: {ent.attributes[attribute]}")
    print()

# Retrieve a single entity
entity: Entity = service.retrieve_single("new_tablename", uuid.UUID("YOUR_GUID"))

# Create a new entity
new_entity: Entity = Entity("new_tablename")
new_entity["new_name"] = "New Entity"

user_id: uuid.UUID = uuid.UUID("USER_GUID")
new_entity["ownerid"] = EntityReference("systemuser", user_id)

service.create(new_entity)
