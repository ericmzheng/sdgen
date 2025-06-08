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


def test_datastructuremodelclass_custom_int_types_xml():
    xml = """
    <IntModel>
        <i8_field>-128</i8_field>
        <u8_field>255</u8_field>
        <i16_field>-32768</i16_field>
        <u16_field>65535</u16_field>
        <i32_field>-2147483648</i32_field>
        <u32_field>4294967295</u32_field>
    </IntModel>
    """
    model = cast(IntModel, DataStructureModel(IntModel).from_xml(xml))
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
    bad_xml = """
    <IntModel>
        <i8_field>-129</i8_field>
        <u8_field>256</u8_field>
        <i16_field>-32769</i16_field>
        <u16_field>65536</u16>
        <i32_field>-2147483649</i32_field>
        <u32_field>4294967296</u32_field>
    </IntModel>
    """
    with pytest.raises(Exception):
        DataStructureModel(IntModel).from_xml(bad_xml)


def test_datastructuremodelclass_custom_int_list_types_xml():
    xml = """
    <IntListModel>
        <i8_list>
            <i8>-128</i8>
            <i8>0</i8>
            <i8>127</i8>
        </i8_list>
        <u8_list>
            <u8>0</u8>
            <u8>128</u8>
            <u8>255</u8>
        </u8_list>
        <i16_list>
            <i16>-32768</i16>
            <i16>0</i16>
            <i16>32767</i16>
        </i16_list>
        <u16_list>
            <u16>0</u16>
            <u16>32768</u16>
            <u16>65535</u16>
        </u16_list>
        <i32_list>
            <i32>-2147483648</i32>
            <i32>0</i32>
            <i32>2147483647</i32>
        </i32_list>
        <u32_list>
            <u32>0</u32>
            <u32>2147483648</u32>
            <u32>4294967295</u32>
        </u32_list>
    </IntListModel>
    """

    class IntListModel(BaseModel):
        i8_list: List[i8]
        u8_list: List[u8]
        i16_list: List[i16]
        u16_list: List[u16]
        i32_list: List[i32]
        u32_list: List[u32]

    model = cast(IntListModel, DataStructureModel(IntListModel).from_xml(xml))
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
    bad_xml = """
    <IntListModel>
        <i8_list><i8>-129</i8></i8_list>
        <u8_list><u8>256</u8></u8_list>
        <i16_list><i16>-32769</i16></i16_list>
        <u16_list><u16>65536</u16></u16_list>
        <i32_list><i32>-2147483649</i32></i32_list>
        <u32_list><u32>4294967296</u32></u32_list>
    </IntListModel>
    """
    with pytest.raises(Exception):
        DataStructureModel(IntListModel).from_xml(bad_xml)
