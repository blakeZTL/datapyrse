# pylint: disable=missing-module-docstring, missing-function-docstring

import pytest
from datapyrse.query import ColumnSet


def test_column_set_with_list():
    column_set = ColumnSet(columns=["name", "email"])
    assert column_set.columns == ["name", "email"]


def test_column_set_with_none():
    with pytest.raises(
        ValueError, match="Columns must be a list of strings or a value of True"
    ):
        ColumnSet(columns=None)  # type: ignore


def test_column_set_with_false():
    with pytest.raises(
        ValueError, match="Columns must be a list of strings or a value of True"
    ):
        ColumnSet(columns=False)


def test_column_set_with_true():
    column_set = ColumnSet(columns=True)
    assert column_set.columns == []


def test_column_set_with_mixed_list():
    with pytest.raises(
        ValueError, match="Columns must be a list of strings or a value of True"
    ):
        ColumnSet(columns=["name", 1, "email"])  # type: ignore
