from typing import List
import uuid
from query import *
from services import ServiceClient


if __name__ == "__main__":

    print("Service client created")
    service_client = ServiceClient(
        tenant_id="2b69d099-dc61-447b-84c8-001733d8be3a",
        resource_url="https://ajt-burst-dev.crm9.dynamics.com",
        prompt="select_account",
    )
    if service_client.IsReady:
        entity: Entity = service_client.retrieve(
            entity_logical_name="burstbpa_requesttype",
            entity_id=uuid.UUID("72A3456E-806D-EF11-A671-001DD8037580"),
            column_set=["burstbpa_name", "burstbpa_state", "ownerid"],
        )

        print(entity.to_dict())

        entity_collection = service_client.retrieve_multiple(
            QueryExpression(
                entity_name="burstbpa_requesttype",
                column_set=ColumnSet(True),
                criteria=FilterExpression(
                    filter_operator=FilterOperator.AND,
                    conditions=[
                        ConditionExpression(
                            attribute_name="burstbpa_name",
                            operator=ConditionOperator.EQUAL,
                            values="Basic",
                        )
                    ],
                ),
            )
        )

        print(entity_collection.to_dict())

    # if __name__ == "__main__":
    # entity = Entity(
    #     entity_logical_name="account",
    #     attributes={
    #         "_ownerid_value": str(uuid.uuid4()),
    #         "_ownerid_value@Microsoft.Dynamics.CRM.associatednavigationproperty": "ownerid",
    #         "_ownerid_value@Microsoft.Dynamics.CRM.lookuplogicalname": "systemuser",
    #         "_ownerid_value@OData.Community.Display.V1.FormattedValue": "James Bradford",
    #     },
    # )
    # print(entity.to_dict())
    # print(entity["ownerid"])
