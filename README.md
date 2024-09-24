# datapyrse

## Overview
`datapyrse` is a Python library designed to mimic the functionality of the Microsoft Dataverse SDK

## Features
- **Data Retrieval**: Easily retrieve data from Dataverse entities.
- **Data Manipulation**: Perform CRUD operations on Dataverse data.
- **Query Building**: Build complex queries to filter and sort data.
- **Integration**: Seamlessly integrate with other data processing libraries.

## Installation
To install `datapyrse`, use pip:

```sh
pip install datapyrse
```

## Usage
```py
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

```


