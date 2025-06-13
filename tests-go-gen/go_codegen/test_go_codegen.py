import os
from pydantic import BaseModel
from sdgen.model import DataStructureModel, i32
from sdgen.go_adapter import GoLanguageAdapter
import pytest

def test_go_codegen():
    # Setup
    test_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(test_dir, "outputs")
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    class Person(BaseModel):
        name: str
        age: int
        id: i32

    go_code = GoLanguageAdapter(DataStructureModel(Person)).generate_definition()
    go_path = os.path.join(outputs_dir, "person.go")
    with open(go_path, "w") as f:
        f.write(go_code)

    # Optionally, you could invoke 'go build' or 'go fmt' here if Go is installed
    # For now, just check that the file was written and contains expected struct
    with open(go_path) as f:
        content = f.read()
        assert f'type {Person.__name__} struct' in content
        assert 'Name string' in content
        assert 'Age int' in content
        assert 'Id int' in content
