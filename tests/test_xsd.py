import re
from typing import Optional

from pydantic import BaseModel

from sdgen import DataStructureModel, i8, u16


def normalize_xsd(xsd: str) -> str:
    # Remove whitespace between tags and normalize for comparison
    return re.sub(r">\s+<", "><", xsd.strip())


def test_xsd_simple_flat():
    class Person(BaseModel):
        name: str
        age: int

    xsd = DataStructureModel(Person).to_xsd()
    assert '<xs:element name="Person" type="PersonType"' in xsd
    assert '<xs:element name="name" type="xs:string"' in xsd
    assert '<xs:element name="age" type="xs:int"' in xsd
    assert 'complexType name="PersonType"' in xsd


def test_xsd_nested():
    class Address(BaseModel):
        street: str
        city: str

    class Person(BaseModel):
        name: str
        address: Address

    xsd = DataStructureModel(Person).to_xsd()
    assert '<xs:element name="address" type="AddressType"' in xsd
    assert '<xs:complexType name="AddressType"' in xsd
    assert '<xs:element name="street" type="xs:string"' in xsd
    assert '<xs:element name="city" type="xs:string"' in xsd


def test_xsd_list_of_nested():
    class Pet(BaseModel):
        name: str

    class Person(BaseModel):
        pets: list[Pet]

    xsd = DataStructureModel(Person).to_xsd()
    assert (
        '<xs:element name="pets" type="PetType" minOccurs="0" maxOccurs="unbounded"'
        in xsd
    )
    assert '<xs:complexType name="PetType"' in xsd
    assert '<xs:element name="name" type="xs:string"' in xsd


def test_xsd_optional_and_list():
    class Pet(BaseModel):
        name: str

    class Person(BaseModel):
        name: str
        pets: Optional[list[Pet]]

    xsd = DataStructureModel(Person).to_xsd()
    assert (
        '<xs:element name="pets" type="PetType" minOccurs="0" maxOccurs="unbounded"'
        in xsd
    )
    assert '<xs:element name="name" type="xs:string"' in xsd


def test_xsd_custom_int_types():
    class Foo(BaseModel):
        a: i8
        b: u16

    xsd = DataStructureModel(Foo).to_xsd()
    assert '<xs:element name="a" type="xs:int"' in xsd
    assert '<xs:element name="b" type="xs:int"' in xsd
