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

## Project Structure
- `src/sdgen/`: Core Python code and language adapters.
- `tests/`: Python unit tests for core logic.
- `tests-cpp-gen/`: Pytest-based C++ codegen and serialization tests.
- `tests-rs-gen/`: Pytest-based Rust codegen and serialization tests.

## Supported Languages
- **C++**: Generates struct, JSON/YAML/XML (de)serialization, and file I/O using nlohmann/json, yaml-cpp, rapidxml.
- **Rust**: Generates struct, JSON/YAML/XML (de)serialization, and file I/O using serde, serde_json, serde_yaml, serde-xml-rs.

## License
MIT
