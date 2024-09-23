from dataclasses import dataclass, field
from typing import List
from typing import List, Union


@dataclass
class ColumnSet:
    columns: Union[List[str], bool, None] = field(default=None)

    def __init__(self, columns: Union[List[str], bool, None] = None) -> None:
        if columns == False:
            raise ValueError("Columns must be a list of strings or a value of True")
        elif not columns:
            columns = None
        else:
            self.columns = columns
