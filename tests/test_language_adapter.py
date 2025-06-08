from typing import List, Optional

import pytest

from sdgen import (
    BaseModel,
    CppLanguageAdapter,
    DataStructureModel,
    DataStructureModelClass,
    LanguageAdapter,
    i32,
    u16,
)


class DummyModel(DataStructureModelClass):
    pass


class DummyAdapter(LanguageAdapter):
    pass


class Person(BaseModel):
    name: str
    age: int
    score: float
    id: i32


class Data(BaseModel):
    values: List[int]
    label: Optional[str]
    ids: List[u16]


def test_generate_definition_not_implemented():
    adapter = DummyAdapter(DummyModel)
    with pytest.raises(NotImplementedError):
        adapter.generate_definition()


def test_cpp_language_adapter_simple():
    model = DataStructureModel(Person)
    adapter = CppLanguageAdapter(model)
    cpp_code = adapter.generate_definition()
    assert "struct Person" in cpp_code
    assert "std::string name;" in cpp_code
    assert "int age;" in cpp_code
    assert "double score;" in cpp_code
    assert "int32_t id;" in cpp_code
    assert "nlohmann::json to_json() const" in cpp_code
    assert "static Person from_json(const nlohmann::json& j)" in cpp_code
    assert "YAML::Node to_yaml() const" in cpp_code
    assert "static Person from_yaml(const YAML::Node& node)" in cpp_code
    assert "std::string to_xml() const" in cpp_code
    assert "static Person from_xml(const std::string& xml_str)" in cpp_code
    assert "inline void to_json_file" in cpp_code
    assert "inline Person from_json_file" in cpp_code
    assert "inline void to_yaml_file" in cpp_code
    assert "inline Person from_yaml_file" in cpp_code
    assert "inline void to_xml_file" in cpp_code
    assert "inline Person from_xml_file" in cpp_code


def test_cpp_language_adapter_lists_and_optionals():
    model = DataStructureModel(Data)
    adapter = CppLanguageAdapter(model)
    cpp_code = adapter.generate_definition()
    assert "std::vector<int> values;" in cpp_code
    assert "std::optional<std::string> label;" in cpp_code
    assert "std::vector<uint16_t> ids;" in cpp_code
    assert "struct Data" in cpp_code
    assert "to_json() const" in cpp_code
    assert "from_json(const nlohmann::json& j)" in cpp_code
    assert "to_yaml() const" in cpp_code
    assert "from_yaml(const YAML::Node& node)" in cpp_code
    assert "to_xml() const" in cpp_code
    assert "from_xml(const std::string& xml_str)" in cpp_code
