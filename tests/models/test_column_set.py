import pytest
from models.column_set import ColumnSet


def test_empty_column_set():
    column_set = ColumnSet()
    assert column_set.columns == None


def test_column_set_with_list():
    column_set = ColumnSet(columns=["name", "email"])
    assert column_set.columns == ["name", "email"]


def test_column_set_with_false():
    with pytest.raises(
        ValueError, match="Columns must be a list of strings or a value of True"
    ):
        column_set = ColumnSet(columns=False)
        assert column_set.columns == None


def test_column_set_with_true():
    column_set = ColumnSet(columns=True)
    assert column_set.columns == True


def test_column_set_with_none():
    column_set = ColumnSet(columns=None)
    assert column_set.columns == None