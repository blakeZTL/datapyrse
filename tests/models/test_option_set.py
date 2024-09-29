from datapyrse.models.option_set import OptionSet


def test_option_set_empty_initialization():
    option_set = OptionSet()
    assert option_set is not None
    assert option_set.value == None
    assert option_set.label == None


def test_option_set_initialization():
    option_set = OptionSet(label="Active", value=1)
    assert option_set is not None
    assert option_set.value == 1
    assert option_set.label == "Active"


def test_option_set_to_dict():
    option_set = OptionSet(label="Active", value=1)
    result_dict = option_set.to_dict()

    expected_dict = {
        "value": 1,
        "label": "Active",
    }

    assert result_dict == expected_dict


def test_option_set_get_option_value():
    option_set = OptionSet(label="Active", value=1)
    assert option_set.get_option_value() == 1


def test_option_set_get_option_label():
    option_set = OptionSet(label="Active", value=1)
    assert option_set.get_option_label() == "Active"
