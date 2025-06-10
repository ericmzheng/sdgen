import os
from pathlib import Path
import subprocess
from typing import Optional
from pydantic import BaseModel
from sdgen import DataStructureModel, JavaLanguageAdapter, i32

def test_java_serialization():
    outputs_dir = Path(__file__).parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    class Person(BaseModel):
        name: str
        age: int
        id: int
    code = JavaLanguageAdapter(DataStructureModel(Person)).generate_definition()
    out_path = outputs_dir / "Person.java"
    with open(out_path, "w") as f:
        f.write(code)
    # Write a minimal Main.java to serialize and print outputs
    main_code = '''
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.dataformat.yaml.*;
public class Main {
    public static void main(String[] args) throws Exception {
        Person p = new Person("Alice", 30, 42);
        System.out.println(p.toJson());
        System.out.println(p.toXml());
        System.out.println(p.toYaml());
    }
}
'''
    main_path = outputs_dir / "Main.java"
    with open(main_path, "w") as f:
        f.write(main_code)
    dep_dir = Path(__file__).parent.parent / "target" / "dependency"
    cp = f"{dep_dir}/*:{outputs_dir}"
    subprocess.run(f"javac -cp {cp} -source 11 -target 11 {out_path} {main_path}", shell=True, check=True)
    result = subprocess.run(f"java -cp {cp} -Dfile.encoding=UTF-8 Main", shell=True, check=True, capture_output=True, text=True).stdout.strip()
    print(result)
    actual_output_path = outputs_dir / "actual_output.txt"
    with open(actual_output_path, "w") as f:
        f.write(result)
    # Compare to expected output
    expected_path = Path(__file__).parent / "expected_output.txt"
    with open(expected_path) as f:
        expected = f.read().strip()
    assert result == expected
