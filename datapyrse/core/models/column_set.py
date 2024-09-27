from dataclasses import dataclass, field
from typing import List
from typing import List, Union


@dataclass
class ColumnSet:
    columns: List[str] = field(default_factory=list)

    def __init__(self, columns: Union[List[str], bool]) -> None:
        if isinstance(columns, bool):
            if columns == False:
                raise ValueError("Columns must be a list of strings or a value of True")
            self.columns = []
        elif isinstance(columns, list):
            self.columns = columns
        else:
            raise ValueError("Columns must be a list of strings or a value of True")
