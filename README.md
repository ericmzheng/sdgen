# sdgen

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/E22jhLt3drt8WmRrmkWM8k/VQWy7y3rUaNYdkQU6h8WFq/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/E22jhLt3drt8WmRrmkWM8k/VQWy7y3rUaNYdkQU6h8WFq/tree/main)

`sdgen` is a Python package for generating strongly-typed data structure definitions and robust serialization/deserialization code in multiple languages, including C++ and Rust. It is designed for schema-driven code generation, round-trip serialization, and easy integration into CI pipelines.

## Features
- **Python installable**: Install via pip and use as a library or CLI.
- **Schema-driven**: Define your data structures as Python (Pydantic) models.
- **Multi-language codegen**: Generate C++ and Rust struct definitions with full JSON, YAML, and XML (de)serialization support.
- **Serialization/Deserialization**: Generated code includes methods for round-trip serialization to/from JSON, YAML, and XML, using best-in-class libraries (nlohmann/json, yaml-cpp, rapidxml for C++; serde, serde_json, serde_yaml, serde-xml-rs for Rust).
- **CI-ready**: Includes pytest-based and CircleCI-compatible test infrastructure for validating codegen and serialization in both C++ and Rust.
- **Extensible**: Add new language adapters by subclassing `LanguageAdapter`.
- **XSD schema generation**: Generate XML Schema Definitions (XSD) for your Pydantic models, including nested models and lists, for XML interoperability and schema validation.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Usage

1. **Define your schema:**
   ```python
   from sdgen import BaseModel, i32
   class Person(BaseModel):
       name: str
       age: int
       id: i32
   ```

2. **Generate code:**
   ```python
   from sdgen import DataStructureModel, CppLanguageAdapter, RustLanguageAdapter
   cpp_code = CppLanguageAdapter(DataStructureModel(Person)).generate_definition()
   rust_code = RustLanguageAdapter(DataStructureModel(Person)).generate_definition()
   ```

3. **Integrate in CI:**
   - Use the provided pytest tests in `tests-cpp-gen/` and `tests-rs-gen/` to validate codegen, compilation, and round-trip serialization for C++ and Rust.
   - CircleCI config is provided for automated testing.

## XSD Schema Generation

`sdgen` supports generating XML Schema Definitions (XSD) for your Pydantic models, including nested models and lists. This is useful for interoperability with XML-based systems and schema validation.

### Usage

Call the `to_xsd()` method on your data structure model to generate an XSD string:

```python
from pydantic import BaseModel
from sdgen import DataStructureModel

class Address(BaseModel):
    street: str
    city: str

class Person(BaseModel):
    name: str
    age: int
    address: Address

xsd_str = DataStructureModel(Person).to_xsd()
print(xsd_str)
```

The generated XSD will include complex types for nested models and handle lists and optional fields appropriately.

## Project Structure
- `src/sdgen/`: Core Python code and language adapters.
- `tests/`: Python unit tests for core logic.
- `tests-cpp-gen/`: Pytest-based C++ codegen and serialization tests.
- `tests-rs-gen/`: Pytest-based Rust codegen and serialization tests.

## Supported Languages
- **C++**: Generates struct, JSON/YAML/XML (de)serialization, and file I/O using nlohmann/json, yaml-cpp, rapidxml.
- **Rust**: Generates struct, JSON/YAML/XML (de)serialization, and file I/O using serde, serde_json, serde_yaml, serde-xml-rs.
- **Java**: Generates struct, JSON/YAML/XML (de)serialization, and file I/O using Jackson.

## Future Languages
- **Go**: Planned support for Go code generation with encoding/json and encoding/xml.
- **C#**: Planned support for C# code generation with Newtonsoft.Json for JSON/YAML and System.Xml.Serialization for XML.
- **Swift**: Planned support for Swift code generation with Codable for JSON/YAML and XML.
- **Ruby**: Planned support for Ruby code generation with JSON and Nokogiri for XML.

## License
MIT
