import os
from pydantic import BaseModel
from sdgen.model import DataStructureModel, i32
from sdgen.swift_adapter import SwiftLanguageAdapter
import pytest

def test_swift_codegen(tmp_path):
    # Setup
    test_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(test_dir, "outputs")
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    class Person(BaseModel):
        name: str
        age: int
        id: i32

    swift_code = SwiftLanguageAdapter(DataStructureModel(Person)).generate_definition()
    swift_path = os.path.join(outputs_dir, "Person.swift")
    with open(swift_path, "w") as f:
        f.write(swift_code)

    # Optionally, you could invoke 'swiftc' here if Swift is installed
    # For now, just check that the file was written and contains expected struct and methods
    with open(swift_path) as f:
        content = f.read()
        assert f'struct {Person.__name__}: Codable' in content
        assert 'var name: String' in content
        assert 'var age: Int' in content
        assert 'var id: Int' in content
        assert 'toJSON()' in content
        assert 'fromJSON' in content
