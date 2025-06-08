import json
from typing import List, Optional, cast

import pytest
from pydantic import BaseModel

from sdgen import DataStructureModel


class Address(BaseModel):
    city: str
    zip_code: str
    apartment: Optional[str] = None


class Person(BaseModel):
    name: str
    age: Optional[int] = None
    hobbies: Optional[List[str]] = None
    address_history: Optional[List[Address]] = None


def test_parse_json():
    data = {
        "name": "Charlie",
        "hobbies": ["Chess", "Cooking"],
        "address_history": [
            {"city": "Denver", "zip_code": "80203"},
            {"city": "Seattle", "zip_code": "98101", "apartment": "5C"},
        ],
    }
    charlie = cast(
        Person, DataStructureModel(Person).parse_json(json.dumps(data))
    )
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


def test_parse_json_minimal():
    data = {"name": "Alice"}
    alice = cast(
        Person, DataStructureModel(Person).parse_json(json.dumps(data))
    )
    assert alice.name == "Alice"
    assert alice.age is None
    assert alice.hobbies is None
    assert alice.address_history is None


def test_parse_json_with_age_and_no_hobbies():
    data = {"name": "Bob", "age": 42}
    bob = cast(Person, DataStructureModel(Person).parse_json(json.dumps(data)))
    assert bob.name == "Bob"
    assert bob.age == 42
    assert bob.hobbies is None
    assert bob.address_history is None


def test_parse_json_empty_hobbies_and_address_history():
    data = {"name": "Dana", "hobbies": [], "address_history": []}
    dana = cast(Person, DataStructureModel(Person).parse_json(json.dumps(data)))
    assert dana.name == "Dana"
    assert dana.hobbies == []
    assert dana.address_history == []


def test_parse_json_address_with_apartment_missing():
    data = {
        "name": "Ed",
        "address_history": [{"city": "Boston", "zip_code": "02101"}],
    }
    ed = cast(Person, DataStructureModel(Person).parse_json(json.dumps(data)))
    assert ed.name == "Ed"
    assert ed.address_history is not None
    assert len(ed.address_history) == 1
    assert ed.address_history[0].city == "Boston"
    assert ed.address_history[0].zip_code == "02101"
    assert ed.address_history[0].apartment is None


def test_parse_json_invalid_json_raises():
    invalid_json = '{"name": "Missing end quote}'
    with pytest.raises(Exception):
        DataStructureModel(Person).parse_json(invalid_json)


def test_parse_json_invalid_age_type_raises():
    data = {"name": "Frank", "age": "notanumber"}
    with pytest.raises(Exception):
        DataStructureModel(Person).parse_json(json.dumps(data))


def test_to_json_and_to_native_tree_roundtrip():
    data = {
        "name": "RoundTrip",
        "age": 25,
        "hobbies": ["A", "B"],
        "address_history": [
            {"city": "X", "zip_code": "12345", "apartment": "1A"}
        ],
    }
    model = DataStructureModel(Person).parse_native_tree(data)
    json_str = model.to_json()
    parsed = cast(Person, DataStructureModel(Person).parse_json(json_str))
    assert parsed.name == "RoundTrip"
    assert parsed.age == 25
    assert parsed.hobbies == ["A", "B"]
    assert parsed.address_history is not None
    assert parsed.address_history[0].city == "X"
    assert parsed.address_history[0].apartment == "1A"
