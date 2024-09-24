import logging
from typing import Any, Tuple
import uuid


def validate_guid(guid: Any) -> Tuple[bool, uuid.UUID]:
    if guid is None:
        logging.error("GUID is required")
        return False, None
    elif guid is not isinstance(guid, uuid.uuid4):
        try:
            guid = uuid.UUID(str(guid))
        except ValueError:
            logging.error(f"Invalid UUID: {guid}")
            return False, None
    return True, guid
