from dataclasses import dataclass, field
from typing import List
from typing import List, Union


@dataclass
class ColumnSet:
    columns: Union[List[str], bool, None] = field(default=None)

    def __init__(self, columns: Union[List[str], bool, None] = None) -> None:
        if isinstance(columns, bool):
            if columns == False:
                raise ValueError("Columns must be a list of strings or a value of True")
            self.columns = columns
        elif isinstance(columns, list):
            self.columns = columns
        elif not isinstance(columns, list) or not isinstance(columns, bool):
            raise ValueError("Columns must be a list of strings or a value of True")
        else:
            self.columns = columns
