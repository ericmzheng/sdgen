from typing import cast

import pytest
from pydantic import BaseModel

from sdgen import DataStructureModel, i8, i16, i32, u8, u16, u32


def test_i8():
    assert i8(-128) == -128
    assert i8(127) == 127
    with pytest.raises(ValueError):
        i8(-129)
    with pytest.raises(ValueError):
        i8(128)


def test_u8():
    assert u8(0) == 0
    assert u8(255) == 255
    with pytest.raises(ValueError):
        u8(-1)
    with pytest.raises(ValueError):
        u8(256)


def test_i16():
    assert i16(-32768) == -32768
    assert i16(32767) == 32767
    with pytest.raises(ValueError):
        i16(-32769)
    with pytest.raises(ValueError):
        i16(32768)


def test_u16():
    assert u16(0) == 0
    assert u16(65535) == 65535
    with pytest.raises(ValueError):
        u16(-1)
    with pytest.raises(ValueError):
        u16(65536)


def test_i32():
    assert i32(-2147483648) == -2147483648
    assert i32(2147483647) == 2147483647
    with pytest.raises(ValueError):
        i32(-2147483649)
    with pytest.raises(ValueError):
        i32(2147483648)


def test_u32():
    assert u32(0) == 0
    assert u32(4294967295) == 4294967295
    with pytest.raises(ValueError):
        u32(-1)
    with pytest.raises(ValueError):
        u32(4294967296)


class IntModel(BaseModel):
    i8_field: i8
    u8_field: u8
    i16_field: i16
    u16_field: u16
    i32_field: i32
    u32_field: u32


def test_datastructuremodelclass_custom_int_types():
    data = {
        "i8_field": -128,
        "u8_field": 255,
        "i16_field": -32768,
        "u16_field": 65535,
        "i32_field": -2147483648,
        "u32_field": 4294967295,
    }
    model = cast(IntModel, DataStructureModel(IntModel).from_native_tree(data))
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
    bad_data = {
        "i8_field": -129,
        "u8_field": 256,
        "i16_field": -32769,
        "u16_field": 65536,
        "i32_field": -2147483649,
        "u32_field": 4294967296,
    }
    with pytest.raises(Exception):
        DataStructureModel(IntModel).from_native_tree(bad_data)
