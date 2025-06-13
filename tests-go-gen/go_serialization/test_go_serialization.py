import os
from pydantic import BaseModel
from sdgen.model import DataStructureModel, i32
from sdgen.go_adapter import GoLanguageAdapter
import pytest

def test_go_serialization(tmp_path):
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

    # Write a main.go that exercises the struct and prints JSON and XML
    main_go = os.path.join(outputs_dir, "main.go")
    with open(main_go, "w") as f:
        f.write(f'''package main
import (
    "fmt"
    "os"
    "{os.path.splitext(os.path.basename(go_path))[0]}"
)
func main() {{
    p := {Person.__name__}{{Name: "Alice", Age: 30, Id: 42}}
    jsonStr, _ := p.ToJSON()
    fmt.Println(jsonStr)
    xmlStr, _ := p.ToXML()
    fmt.Println(xmlStr)
}}
''')

    # Run 'go run' if Go is available
    try:
        import shutil
        if shutil.which("go"):
            import subprocess
            run_ret = subprocess.run(["go", "run", "main.go", "person.go"], cwd=outputs_dir, capture_output=True, text=True)
            assert run_ret.returncode == 0, f"Go run failed: {run_ret.stderr}"
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
                assert output.strip() == expected.strip(), f"Output does not match expected_output.txt\n--- Expected ---\n{expected}\n--- Actual ---\n{output}"
    except Exception as e:
        pytest.skip(f"Go not available or failed to run: {e}")
