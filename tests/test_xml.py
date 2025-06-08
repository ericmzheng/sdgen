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


def test_parse_xml():
    xml = """
    <Person>
      <name>Charlie</name>
      <hobbies>
        <str>Chess</str>
        <str>Cooking</str>
      </hobbies>
      <address_history>
        <Address>
          <city>Denver</city>
          <zip_code>80203</zip_code>
        </Address>
        <Address>
          <city>Seattle</city>
          <zip_code>98101</zip_code>
          <apartment>5C</apartment>
        </Address>
      </address_history>
    </Person>
    """
    charlie = cast(Person, DataStructureModel(Person).from_xml(xml))
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


def test_parse_minimal():
    xml = """
    <Person>
        <name>Alice</name>
    </Person>
    """
    alice = cast(Person, DataStructureModel(Person).from_xml(xml))
    assert alice.name == "Alice"
    assert alice.age is None
    assert alice.hobbies is None
    assert alice.address_history is None


def test_parse_with_age_and_no_hobbies():
    xml = """
    <Person>
        <name>Bob</name>
        <age>42</age>
    </Person>
    """
    bob = cast(Person, DataStructureModel(Person).from_xml(xml))
    assert bob.name == "Bob"
    assert bob.age == 42
    assert bob.hobbies is None
    assert bob.address_history is None


def test_parse_empty_hobbies_and_address_history():
    xml = """
    <Person>
        <name>Dana</name>
        <hobbies></hobbies>
        <address_history></address_history>
    </Person>
    """
    dana = cast(Person, DataStructureModel(Person).from_xml(xml))
    assert dana.name == "Dana"
    assert dana.hobbies == []
    assert dana.address_history == []


def test_parse_address_with_apartment_missing():
    xml = """
    <Person>
        <name>Ed</name>
        <address_history>
            <Address>
                <city>Boston</city>
                <zip_code>02101</zip_code>
            </Address>
        </address_history>
    </Person>
    """
    ed = cast(Person, DataStructureModel(Person).from_xml(xml))
    assert ed.name == "Ed"
    assert ed.address_history is not None
    assert len(ed.address_history) == 1
    assert ed.address_history[0].city == "Boston"
    assert ed.address_history[0].zip_code == "02101"
    assert ed.address_history[0].apartment is None


def test_parse_invalid_xml_raises():
    xml = "<Person><name>Missing end tag"
    with pytest.raises(Exception):
        DataStructureModel(Person).from_xml(xml)


def test_parse_invalid_age_type_raises():
    xml = """
    <Person>
        <name>Frank</name>
        <age>notanumber</age>
    </Person>
    """
    with pytest.raises(Exception):
        DataStructureModel(Person).from_xml(xml)


def test_to_xml_and_roundtrip():
    data = {
        "name": "RoundTrip",
        "age": 25,
        "hobbies": ["A", "B"],
        "address_history": [
            {"city": "X", "zip_code": "12345", "apartment": "1A"}
        ],
    }
    model = DataStructureModel(Person).from_native_tree(data)
    xml_str = model.to_xml()
    parsed = cast(Person, DataStructureModel(Person).from_xml(xml_str))
    assert parsed.name == "RoundTrip"
    assert parsed.age == 25
    assert parsed.hobbies == ["A", "B"]
    assert parsed.address_history is not None
    assert parsed.address_history[0].city == "X"
    assert parsed.address_history[0].apartment == "1A"
