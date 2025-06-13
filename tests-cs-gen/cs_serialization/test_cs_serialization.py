import os
from pydantic import BaseModel
from sdgen.model import DataStructureModel, i32
from sdgen.cs_adapter import CsLanguageAdapter
import subprocess
import pytest

def test_cs_serialization(tmp_path):
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

    # Write a Program.cs that exercises the class and prints JSON, XML, and YAML
    main_cs = os.path.join(outputs_dir, "Program.cs")
    with open(main_cs, "w") as f:
        f.write(f'''using System;\nusing YamlDotNet.Serialization;\nclass Program {{\n    static void Main() {{\n        var p = new Person {{ name = \"Alice\", age = 30, id = 42 }};\n        Console.WriteLine(p.ToJson());\n        Console.WriteLine(p.ToXml());\n        var serializer = new SerializerBuilder().Build();\n        var yaml = serializer.Serialize(p);\n        Console.WriteLine(yaml);\n    }}\n}}\n''')

    # Add YamlDotNet to the project
    csproj_path = os.path.join(outputs_dir, "TestCsGen.csproj")
    with open(csproj_path, "w") as f:
        f.write('<Project Sdk="Microsoft.NET.Sdk">\n  <PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net8.0</TargetFramework>\n  </PropertyGroup>\n  <ItemGroup>\n    <PackageReference Include="YamlDotNet" Version="13.1.1" />\n  </ItemGroup>\n</Project>')
    # Compile and run
    run_ret = subprocess.run(["dotnet", "run", "--project", csproj_path], cwd=outputs_dir, capture_output=True, text=True)
    assert run_ret.returncode == 0, f"dotnet run failed: {run_ret.stderr}"
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
