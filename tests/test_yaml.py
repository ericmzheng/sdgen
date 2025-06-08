from typing import List, Optional, cast

import pytest
from pydantic import BaseModel

from sdgen import DataStructureModel, i8, i16, i32, u8, u16, u32


class Address(BaseModel):
    city: str
    zip_code: str
    apartment: Optional[str] = None


class Person(BaseModel):
    name: str
    age: Optional[int] = None
    hobbies: Optional[List[str]] = None
    address_history: Optional[List[Address]] = None


class IntModel(BaseModel):
    i8_field: i8
    u8_field: u8
    i16_field: i16
    u16_field: u16
    i32_field: i32
    u32_field: u32


class IntListModel(BaseModel):
    i8_list: list[i8]
    u8_list: list[u8]
    i16_list: list[i16]
    u16_list: list[u16]
    i32_list: list[i32]
    u32_list: list[u32]


def test_parse_yaml():
    yaml_data = """
    name: Charlie
    hobbies:
      - Chess
      - Cooking
    address_history:
      - city: Denver
        zip_code: "80203"
      - city: Seattle
        zip_code: "98101"
        apartment: 5C
    """
    charlie = cast(Person, DataStructureModel(Person).from_yaml(yaml_data))
    assert charlie.name == "Charlie"
    assert charlie.age is None
    assert charlie.hobbies == ["Chess", "Cooking"]
    assert charlie.address_history is not None
    assert len(charlie.address_history) == 2
    assert charlie.address_history[0].city == "Denver"
    assert charlie.address_history[0].zip_code == "80203"
    assert charlie.address_history[0].apartment is None
    assert charlie.address_history[1].city == "Seattle"
    assert charlie.address_history[1].zip_code == "98101"
    assert charlie.address_history[1].apartment == "5C"


def test_parse_yaml_minimal():
    yaml_data = """
    name: Alice
    """
    alice = cast(Person, DataStructureModel(Person).from_yaml(yaml_data))
    assert alice.name == "Alice"
    assert alice.age is None
    assert alice.hobbies is None
    assert alice.address_history is None


def test_parse_yaml_with_age_and_no_hobbies():
    yaml_data = """
    name: Bob
    age: 42
    """
    bob = cast(Person, DataStructureModel(Person).from_yaml(yaml_data))
    assert bob.name == "Bob"
    assert bob.age == 42
    assert bob.hobbies is None
    assert bob.address_history is None


def test_parse_yaml_empty_hobbies_and_address_history():
    yaml_data = """
    name: Dana
    hobbies: []
    address_history: []
    """
    dana = cast(Person, DataStructureModel(Person).from_yaml(yaml_data))
    assert dana.name == "Dana"
    assert dana.hobbies == []
    assert dana.address_history == []


def test_parse_yaml_address_with_apartment_missing():
    yaml_data = """
    name: Ed
    address_history:
      - city: Boston
        zip_code: "02101"
    """
    ed = cast(Person, DataStructureModel(Person).from_yaml(yaml_data))
    assert ed.name == "Ed"
    assert ed.address_history is not None
    assert len(ed.address_history) == 1
    assert ed.address_history[0].city == "Boston"
    assert ed.address_history[0].zip_code == "02101"
    assert ed.address_history[0].apartment is None


def test_parse_yaml_invalid_yaml_raises():
    yaml_data = "name: [unclosed"
    with pytest.raises(Exception):
        DataStructureModel(Person).from_yaml(yaml_data)


def test_parse_yaml_invalid_age_type_raises():
    yaml_data = """
    name: Frank
    age: notanumber
    """
    with pytest.raises(Exception):
        DataStructureModel(Person).from_yaml(yaml_data)


def test_to_yaml_and_roundtrip():
    data = {
        "name": "RoundTrip",
        "age": 25,
        "hobbies": ["A", "B"],
        "address_history": [
            {"city": "X", "zip_code": "12345", "apartment": "1A"}
        ],
    }
    model = DataStructureModel(Person).from_native_tree(data)
    yaml_str = model.to_yaml()
    parsed = cast(Person, DataStructureModel(Person).from_yaml(yaml_str))
    assert parsed.name == "RoundTrip"
    assert parsed.age == 25
    assert parsed.hobbies == ["A", "B"]
    assert parsed.address_history is not None
    assert parsed.address_history[0].city == "X"
    assert parsed.address_history[0].apartment == "1A"


def test_datastructuremodelclass_custom_int_types_yaml():
    yaml_data = """
    i8_field: -128
    u8_field: 255
    i16_field: -32768
    u16_field: 65535
    i32_field: -2147483648
    u32_field: 4294967295
    """
    model = cast(IntModel, DataStructureModel(IntModel).from_yaml(yaml_data))
    assert isinstance(model.i8_field, i8)
    assert model.i8_field == -128
    assert isinstance(model.u8_field, u8)
    assert model.u8_field == 255
    assert isinstance(model.i16_field, i16)
    assert model.i16_field == -32768
    assert isinstance(model.u16_field, u16)
    assert model.u16_field == 65535
    assert isinstance(model.i32_field, i32)
    assert model.i32_field == -2147483648
    assert isinstance(model.u32_field, u32)
    assert model.u32_field == 4294967295
    # Test validation errors
    bad_yaml = """
    i8_field: -129
    u8_field: 256
    i16_field: -32769
    u16_field: 65536
    i32_field: -2147483649
    u32_field: 4294967296
    """
    with pytest.raises(Exception):
        DataStructureModel(IntModel).from_yaml(bad_yaml)


def test_datastructuremodelclass_custom_int_list_types_yaml():
    class IntListModel(BaseModel):
        i8_list: List[i8]
        u8_list: List[u8]
        i16_list: List[i16]
        u16_list: List[u16]
        i32_list: List[i32]
        u32_list: List[u32]

    yaml_data = """
    i8_list:
      - -128
      - 0
      - 127
    u8_list:
      - 0
      - 128
      - 255
    i16_list:
      - -32768
      - 0
      - 32767
    u16_list:
      - 0
      - 32768
      - 65535
    i32_list:
      - -2147483648
      - 0
      - 2147483647
    u32_list:
      - 0
      - 2147483648
      - 4294967295
    """
    model = cast(
        IntListModel, DataStructureModel(IntListModel).from_yaml(yaml_data)
    )
    assert model.i8_list == [-128, 0, 127]
    assert all(isinstance(x, i8) for x in model.i8_list)
    assert model.u8_list == [0, 128, 255]
    assert all(isinstance(x, u8) for x in model.u8_list)
    assert model.i16_list == [-32768, 0, 32767]
    assert all(isinstance(x, i16) for x in model.i16_list)
    assert model.u16_list == [0, 32768, 65535]
    assert all(isinstance(x, u16) for x in model.u16_list)
    assert model.i32_list == [-2147483648, 0, 2147483647]
    assert all(isinstance(x, i32) for x in model.i32_list)
    assert model.u32_list == [0, 2147483648, 4294967295]
    assert all(isinstance(x, u32) for x in model.u32_list)
    # Test validation errors
    bad_yaml = """
    i8_list: [-129]
    u8_list: [256]
    i16_list: [-32769]
    u16_list: [65536]
    i32_list: [-2147483649]
    u32_list: [4294967296]
    """
    with pytest.raises(Exception):
        DataStructureModel(IntListModel).from_yaml(bad_yaml)
