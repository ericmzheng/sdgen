import sys
import subprocess
from pydantic import BaseModel
from sdgen import DataStructureModel, CppLanguageAdapter, i32
import os
import pytest

def test_cpp_codegen():
    # Setup
    test_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(test_dir, "outputs")
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    class Person(BaseModel):
        name: str
        age: int
        id: i32

    cpp = CppLanguageAdapter(DataStructureModel(Person)).generate_definition()
    cpp_path = os.path.join(outputs_dir, "Person.h")
    with open(cpp_path, "w") as f:
        f.write(cpp)

    main_cpp = os.path.join(outputs_dir, "main.cpp")
    with open(main_cpp, "w") as f:
        f.write('#include <iostream>\n')
        f.write('#include "Person.h"\n')
        f.write('int main() { Person p; p.name = "Alice"; p.age = 30; p.id = 42; std::cout << p.to_json().dump(2) << std::endl; return 0; }\n')

    ret = subprocess.run(["g++", "-std=c++17", "-o", os.path.join(outputs_dir, "test_cpp"), main_cpp], cwd=outputs_dir, capture_output=True)
    assert ret.returncode == 0, f"g++ failed: {ret.stderr.decode()}"
