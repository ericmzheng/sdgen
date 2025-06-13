import os
from pydantic import BaseModel
from sdgen.model import DataStructureModel, i32
from sdgen.cs_adapter import CsLanguageAdapter
import pytest

def test_cs_codegen(tmp_path):
    # Setup
    test_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(test_dir, "outputs")
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    class Person(BaseModel):
        name: str
        age: int
        id: i32

    cs_code = CsLanguageAdapter(DataStructureModel(Person)).generate_definition()
    cs_path = os.path.join(outputs_dir, "Person.cs")
    with open(cs_path, "w") as f:
        f.write(cs_code)

    # Optionally, you could invoke 'dotnet build' here if .NET is installed
    # For now, just check that the file was written and contains expected class and methods
    with open(cs_path) as f:
        content = f.read()
        assert f'public class {Person.__name__}' in content
        assert 'public string name' in content
        assert 'public int age' in content
        assert 'public int id' in content
        assert 'ToJson()' in content
        assert 'ToXml()' in content
