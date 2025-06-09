import sys
import subprocess
from sdgen import BaseModel, DataStructureModel, CppLanguageAdapter, i32
import os
import pytest

def test_cpp_serialization(tmp_path):
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
        f.write('int main() { Person p; p.name = "Alice"; p.age = 30; p.id = 42; std::cout << p.to_json().dump(2) << std::endl; std::string xml = p.to_xml(); std::cout << xml << std::endl; auto p2 = Person::from_xml(xml); std::cout << p2.name << "," << p2.age << "," << p2.id << std::endl; return 0; }\n')

    ret = subprocess.run(["g++", "-std=c++17", "-o", os.path.join(outputs_dir, "test_cpp"), main_cpp, "-lyaml-cpp"], cwd=outputs_dir, capture_output=True)
    assert ret.returncode == 0, f"g++ failed: {ret.stderr.decode()}"

    run_ret = subprocess.run([os.path.join(outputs_dir, "test_cpp")], cwd=outputs_dir, capture_output=True, text=True)
    assert run_ret.returncode == 0, f"C++ binary failed: {run_ret.stderr}"

    # Save actual output
    actual_output_path = os.path.join(outputs_dir, "actual_output.txt")
    with open(actual_output_path, "w") as f:
        f.write(run_ret.stdout)

    # Compare to expected output if present
    expected_output_path = os.path.join(test_dir, "expected_output.txt")
    if os.path.exists(expected_output_path):
        with open(expected_output_path) as f:
            expected = f.read()
        assert run_ret.stdout.strip() == expected.strip(), f"Output does not match expected_output.txt\n--- Expected ---\n{expected}\n--- Actual ---\n{run_ret.stdout}"
