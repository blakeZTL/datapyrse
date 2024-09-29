"""
A module for creating column sets for queries
"""

from dataclasses import dataclass, field
from typing import Union


@dataclass
class ColumnSet:
    """
    Represents a set of columns to include in a query.

    This class encapsulates the structure and behavior of a column set in a query,
    including the list of columns to include in the query.

    Attributes:
        columns (Union[list[str], bool]): A list of column names to include in the
            query, or a boolean value indicating whether to include all columns.

    Raises:
        ValueError: If columns are not provided or are not a list of strings or a
            boolean value
    """

    columns: Union[list[str], bool] = field(default_factory=list)

    def __post_init__(
        self,
    ) -> None:
        if not self.columns:
            raise ValueError("Columns must be a list of strings or a value of True")
        if isinstance(self.columns, bool):
            if self.columns is False:
                raise ValueError("Columns must be a list of strings or a value of True")
            self.columns = []
