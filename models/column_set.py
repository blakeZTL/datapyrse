from dataclasses import dataclass, field
from typing import List


@dataclass
class ColumnSet:
    all_columns: bool = False
    columns: List[str] = field(default_factory=list)
