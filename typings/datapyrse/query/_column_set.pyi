from dataclasses import dataclass

@dataclass
class ColumnSet:
    columns: list[str] | bool = ...
    def __post_init__(self) -> None: ...
    def __init__(self, columns=...) -> None: ...
