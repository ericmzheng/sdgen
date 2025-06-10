import sys
import subprocess
from pydantic import BaseModel
from sdgen import DataStructureModel, RustLanguageAdapter, i32
import os
import pytest

def test_rust_serialization():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(test_dir, "outputs")
    src_dir = os.path.join(outputs_dir, "src")
    os.makedirs(src_dir, exist_ok=True)

    class Person(BaseModel):
        name: str
        age: int
        id: i32

    rust = RustLanguageAdapter(DataStructureModel(Person)).generate_definition()
    person_rs = os.path.join(src_dir, "person.rs")
    with open(person_rs, "w") as f:
        f.write(rust)

    main_rs = os.path.join(src_dir, "main.rs")
    main_code = '''extern crate serde_xml_rs;
mod person;
use person::*;
fn main() {
    let p = Person { name: "Alice".to_string(), age: 30, id: 42 };
    println!("{}", p.to_json());
    let xml = serde_xml_rs::to_string(&p).unwrap();
    println!("{}", xml);
    let p2: Person = serde_xml_rs::from_str(&xml).unwrap();
    println!("{},{},{}", p2.name, p2.age, p2.id);
}
'''
    with open(main_rs, "w") as f:
        f.write(main_code)

    cargo_toml = os.path.join(outputs_dir, "Cargo.toml")
    with open(cargo_toml, "w") as f:
        f.write('[package]\nname = "person_test"\nversion = "0.1.0"\nedition = "2021"\n')
        f.write('\n[dependencies]\nserde = { version = "1.0", features = ["derive"] }\nserde_json = "1.0"\nserde_yaml = "0.9"\nserde-xml-rs = "0.6"\n')

    ret = subprocess.run(["cargo", "build"], cwd=outputs_dir, capture_output=True)
    assert ret.returncode == 0, f"cargo build failed: {ret.stderr.decode()}"
    run_ret = subprocess.run(["cargo", "run", "--quiet"], cwd=outputs_dir, capture_output=True, text=True)
    assert run_ret.returncode == 0, f"cargo run failed: {run_ret.stderr}"
    actual_output_path = os.path.join(outputs_dir, "actual_output.txt")
    with open(actual_output_path, "w") as f:
        f.write(run_ret.stdout)
    expected_output_path = os.path.join(test_dir, "expected_output.txt")
    if os.path.exists(expected_output_path):
        with open(expected_output_path) as f:
            expected = f.read()
        assert run_ret.stdout.strip() == expected.strip(), f"Output does not match expected_output.txt\n--- Expected ---\n{expected}\n--- Actual ---\n{run_ret.stdout}"
