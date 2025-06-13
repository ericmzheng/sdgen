import os
from pydantic import BaseModel
from sdgen.model import DataStructureModel, i32
from sdgen.swift_adapter import SwiftLanguageAdapter
import subprocess
import pytest
import json

def test_swift_serialization(tmp_path):
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

    # Write a main.swift that exercises the struct and prints JSON, XML, and YAML
    main_swift = os.path.join(outputs_dir, "main.swift")
    main_swift_code = (
        "import Foundation\n"
        "import XMLCoder\n"
        "import Yams\n\n"
        "let p = Person(name: \"Alice\", age: 30, id: 42)\n"
        "// JSON\n"
        "guard let json = p.toJSON() else { fatalError(\"JSON serialization failed\") }\n"
        "print(json)\n"
        "// XML\n"
        "guard let xml = try? XMLEncoder().encode(p, withRootKey: \"Person\", header: XMLHeader(version: 1.0)) else { fatalError(\"XML serialization failed\") }\n"
        "print(String(data: xml, encoding: .utf8)!)\n"
        "// YAML\n"
        "guard let yaml = try? YAMLEncoder().encode(p) else { fatalError(\"YAML serialization failed\") }\n"
        "print(yaml)\n"
    )
    with open(main_swift, "w") as f:
        f.write(main_swift_code)

    # Concatenate Person.swift and main.swift into combined.swift
    combined_swift = os.path.join(outputs_dir, "combined.swift")
    with open(combined_swift, "w") as outfile:
        for fname in [swift_path, main_swift]:
            with open(fname) as infile:
                outfile.write(infile.read())
                outfile.write("\n")

    # Move combined.swift to Sources/SwiftSerializationTest/main.swift under tests-swift-gen
    sources_dir = os.path.join(os.path.dirname(test_dir), "Sources", "SwiftSerializationTest")
    os.makedirs(sources_dir, exist_ok=True)
    main_swift_path = os.path.join(sources_dir, "main.swift")
    os.rename(combined_swift, main_swift_path)

    # Run 'swift build' and 'swift run' in tests-swift-gen
    swift_root = os.path.dirname(test_dir)
    build_ret = subprocess.run(["swift", "build"], cwd=swift_root, capture_output=True, text=True)
    assert build_ret.returncode == 0, f"Swift build failed: {build_ret.stderr}"
    run_ret = subprocess.run(["swift", "run"], cwd=swift_root, capture_output=True, text=True)
    assert run_ret.returncode == 0, f"Swift run failed: {run_ret.stderr}"
    output = run_ret.stdout
    # Save actual output
    actual_output_path = os.path.join(outputs_dir, "actual_output.txt")
    with open(actual_output_path, "w") as f:
        f.write(output)
    # Compare to expected output if present
    expected_output_path = os.path.join(test_dir, "expected_output.txt")
    if os.path.exists(expected_output_path):
        with open(expected_output_path) as f:
            expected = f.read()
        # Split outputs into lines
        output_lines = output.strip().splitlines()
        expected_lines = expected.strip().splitlines()
        # Compare JSON (first 5 lines)
        output_json = "\n".join(output_lines[:5])
        expected_json = "\n".join(expected_lines[:5])
        assert json.loads(output_json) == json.loads(expected_json), (
            f"JSON output does not match expected (order-insensitive)\n--- Expected ---\n{expected_json}\n--- Actual ---\n{output_json}")
        # Compare the rest as string
        assert "\n".join(output_lines[5:]).strip() == "\n".join(expected_lines[5:]).strip(), (
            f"Non-JSON output does not match expected\n--- Expected ---\n{expected}\n--- Actual ---\n{output}")
