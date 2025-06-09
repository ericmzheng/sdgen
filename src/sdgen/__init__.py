from __future__ import annotations

import functools
import json
import os
from typing import Any, Dict, List, Type, Union, get_args, get_origin
from xml.etree.ElementTree import Element, fromstring, parse, tostring

import yaml
from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler, create_model
from pydantic_core import core_schema

__all__ = ["DataStructureModel"]


class _sdgenint(int):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ):
        # Accept int or this type, coerce to this type, and validate range
        def validate(value):
            v = int(value)
            # Range check is done in __new__
            return cls(v)

        return core_schema.no_info_plain_validator_function(validate)


class i8(_sdgenint):
    def __new__(cls, value):
        value = int(value)
        if not -128 <= value <= 127:
            raise ValueError("Value out of range for i8")
        return int.__new__(cls, value)


class u8(_sdgenint):
    def __new__(cls, value):
        value = int(value)
        if not 0 <= value <= 255:
            raise ValueError("Value out of range for u8")
        return int.__new__(cls, value)


class i16(_sdgenint):
    def __new__(cls, value):
        value = int(value)
        if not -32768 <= value <= 32767:
            raise ValueError("Value out of range for i16")
        return int.__new__(cls, value)


class u16(_sdgenint):
    def __new__(cls, value):
        value = int(value)
        if not 0 <= value <= 65535:
            raise ValueError("Value out of range for u16")
        return int.__new__(cls, value)


class i32(_sdgenint):
    def __new__(cls, value):
        value = int(value)
        if not -2147483648 <= value <= 2147483647:
            raise ValueError("Value out of range for i32")
        return int.__new__(cls, value)


class u32(_sdgenint):
    def __new__(cls, value):
        value = int(value)
        if not 0 <= value <= 4294967295:
            raise ValueError("Value out of range for u32")
        return int.__new__(cls, value)


def is_custom_int_type(annotation: Type) -> bool:
    """Check if the annotation is a custom integer type."""
    return annotation in (i8, u8, i16, u16, i32, u32)


def is_list_type(annotation: Type) -> bool:
    """Check if the annotation is a list type."""
    return get_origin(annotation) is list


def is_optional_type(annotation: Type) -> bool:
    """Check if the annotation is an optional type."""
    return get_origin(annotation) is Union and type(None) in get_args(
        annotation
    )


def unwrap_list(annotation: Type) -> Type:
    """Unwraps the List type to get the actual type."""
    if is_list_type(annotation):
        return get_args(annotation)[0]
    return annotation


def unwrap_optional(annotation: Type) -> Type:
    """Unwraps the Optional type to get the actual type."""
    if is_optional_type(annotation):
        return next(
            arg for arg in get_args(annotation) if arg is not type(None)
        )
    return annotation


class DataStructureModelClass(BaseModel):
    """
    A base class for data structure models.
    This class can be extended to create specific data structure models.
    Provides serialization and deserialization methods for XML, JSON, and YAML.
    """

    @classmethod
    def _model(cls) -> Type[BaseModel]:
        """
        Returns the Pydantic model class associated with this data structure model.
        This method must be implemented by subclasses to return the specific Pydantic model class.
        """
        raise NotImplementedError(
            "Subclasses must implement the _model method to return the Pydantic model class."
        )

    @classmethod
    def from_xml_file(cls, path: os.PathLike) -> DataStructureModelClass:
        """
        Deserializes an XML file into an instance of the model.
        """
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_xml_tree(parse(f).getroot())

    @classmethod
    def from_xml(cls, xml_data: str) -> DataStructureModelClass:
        """
        Deserializes an XML string into an instance of the model.
        """
        return cls.from_xml_tree(fromstring(xml_data))

    @classmethod
    def from_xml_tree(cls, element: Element) -> DataStructureModelClass:
        """
        Deserializes an XML tree into an instance of the model.
        """
        values = {}
        for name, field in cls._model().model_fields.items():
            annotation = field.annotation
            if annotation is None:
                raise TypeError(f"Cannot determine type for field {name}")
            actual_type = unwrap_optional(annotation)

            values[name] = None

            if is_list_type(actual_type):
                item_type = unwrap_list(actual_type)
                if item_type is None:
                    raise TypeError(
                        f"Cannot determine type for list item in field {name}"
                    )

                list_element = element.find(name)
                if list_element is not None:
                    values[name] = []
                    for item_element in list_element:
                        if item_element.tag != item_type.__name__:
                            raise ValueError(
                                f"Expected item of type {item_type.__name__} in field {name}, "
                                f"but found {item_element.tag}"
                            )

                        if isinstance(item_type, type) and issubclass(
                            item_type, BaseModel
                        ):
                            values[name].append(
                                DataStructureModel(item_type).from_xml_tree(
                                    item_element
                                )
                            )

                        else:
                            values[name].append(item_type(item_element.text))

            elif isinstance(actual_type, type) and issubclass(
                actual_type, BaseModel
            ):
                sub_element = element.find(name)
                if sub_element is not None:
                    values[name] = DataStructureModel(
                        actual_type
                    ).from_xml_tree(sub_element)

            elif isinstance(actual_type, type):
                sub_element = element.find(name)
                if sub_element is not None:
                    values[name] = actual_type(sub_element.text)

        return cls(**values)

    @classmethod
    def from_json_file(cls, path: os.PathLike) -> DataStructureModelClass:
        """
        Deserializes a JSON file into an instance of the model.
        """
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_native_tree(json.load(f))

    @classmethod
    def from_json(cls, json_data: str) -> DataStructureModelClass:
        """
        Deserializes a JSON string into an instance of the model.
        """
        return cls.from_native_tree(json.loads(json_data))

    @classmethod
    def from_native_tree(cls, data: Dict[str, Any]) -> DataStructureModelClass:
        """
        Deserializes a Dict tree into an instance of the model.
        """
        return cls.model_validate(data)

    @classmethod
    def from_yaml_file(cls, path: os.PathLike) -> DataStructureModelClass:
        """
        Deserializes a YAML file into an instance of the model.
        """
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_native_tree(yaml.safe_load(f))

    @classmethod
    def from_yaml(cls, yaml_data: str) -> DataStructureModelClass:
        """
        Deserializes a YAML string into an instance of the model.
        """
        return cls.from_native_tree(yaml.safe_load(yaml_data))

    def to_native_tree(self) -> Dict[str, Any]:
        """
        Serializes the model instance to a native Python dictionary.
        """
        return self.model_dump()

    def to_xml_tree(self) -> Element:
        """
        Serializes the model instance to an XML Element.
        This method is used internally for XML serialization.
        """

        root = Element(self._model().__name__)
        for name, field in self._model().model_fields.items():
            annotation = field.annotation
            if annotation is None:
                raise TypeError(f"Cannot determine type for field {name}")
            actual_type = unwrap_optional(annotation)

            value = getattr(self, name, None)

            if is_list_type(actual_type):
                list_element = Element(name)
                if value is not None:
                    for item in value:
                        if isinstance(item, DataStructureModelClass):
                            item_element = item.to_xml_tree()
                        else:
                            item_element = Element(item.__class__.__name__)
                            item_element.text = str(item)
                        list_element.append(item_element)
                root.append(list_element)

            elif isinstance(actual_type, type) and issubclass(
                actual_type, DataStructureModelClass
            ):
                sub_element = value.to_xml_tree() if value else Element(name)
                root.append(sub_element)

            else:
                element = Element(name)
                element.text = str(value) if value is not None else ""
                root.append(element)

        return root

    def to_xml(self) -> str:
        """
        Serializes the model instance to an XML string.
        """

        return tostring(self.to_xml_tree(), encoding="unicode")

    def to_xml_file(self, path: os.PathLike) -> None:
        """
        Serializes the model instance to an XML file.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_xml())

    def to_json(self) -> str:
        """
        Serializes the model instance to a JSON string.
        """
        return self.model_dump_json()

    def to_json_file(self, path: os.PathLike) -> None:
        """
        Serializes the model instance to a JSON file.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    def to_yaml(self) -> str:
        """
        Serializes the model instance to a YAML string.
        """
        return yaml.dump(self.model_dump(), allow_unicode=True)

    def to_yaml_file(self, path: os.PathLike) -> None:
        """
        Serializes the model instance to a YAML file.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())


@functools.cache
def DataStructureModel(
    base_model: Type[BaseModel],
) -> Type[DataStructureModelClass]:
    """
    Factory function to create a data structure model class based on a Pydantic model.
    This function returns a new class that extends `DataStructureModelClass` and
    provides the `model_cls` attribute to return the provided Pydantic model.
    """

    if not issubclass(base_model, BaseModel):
        raise TypeError("base_model must be a subclass of pydantic.BaseModel")

    if issubclass(base_model, DataStructureModelClass):
        raise TypeError(
            "base_model must not be a subclass of DataStructureModelClass"
        )

    def transform_type(t: Any):
        """
        Transform the type of a field within the BaseModel.
        """
        origin = get_origin(t)
        args = get_args(t)

        if isinstance(t, type) and issubclass(t, BaseModel):
            return DataStructureModel(t)

        if origin in (list, List):
            return List[transform_type(args[0])]
        if origin in (dict, Dict):
            return Dict[args[0], transform_type(args[1])]
        if origin is Union:
            return Union[tuple(transform_type(arg) for arg in args)]
        return t

    new_fields = {}
    for (
        name,
        field,
    ) in base_model.model_fields.items():
        new_field = transform_type(field.annotation)
        default = field.default
        new_fields[name] = (new_field, default)

    new_type = create_model(
        f"{base_model.__name__}DataStructureModel",
        __base__=DataStructureModelClass,
        __config__=ConfigDict(extra="forbid", validate_assignment=True),
        __module__=__name__,
        **new_fields,
    )

    # Set the _model classmethod after class creation to avoid it being a field
    setattr(new_type, "_model", classmethod(lambda cls: base_model))
    return new_type


class LanguageAdapter:
    def __init__(self, model: Type[DataStructureModelClass]):
        self.model = model

    def generate_definition(self) -> str:
        """
        Generate the language-specific data structure definition, including code for
        serialization and deserialization for XML, JSON, and YAML. Serialization and
        deserialization inputs and outputs include string and file.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_definition, which should include all serialization/deserialization code."
        )


class CppLanguageAdapter(LanguageAdapter):
    def generate_definition(self) -> str:
        """
        Generate a C++ struct definition and serialization/deserialization code for XML (RapidXML),
        JSON (nlohmann/json), and YAML (yaml-cpp). Includes string and file I/O.
        """
        model = self.model._model()
        lines = [
            "#include <string>",
            "#include <vector>",
            "#include <fstream>",
            "#include <sstream>",
            "#include <nlohmann/json.hpp>",
            "#include <yaml-cpp/yaml.h>",
            "#include <rapidxml/rapidxml.hpp>",
            "#include <rapidxml/rapidxml_print.hpp>",
            "using std::string; using std::vector;",
            "",
        ]
        # Struct definition
        lines.append(f"struct {model.__name__} {{")
        for name, field in model.model_fields.items():
            annotation = field.annotation
            type_str = self._cpp_type_str(annotation)
            lines.append(f"    {type_str} {name};")
        lines.append("")
        # JSON serialization
        lines.append("    nlohmann::json to_json() const {")
        lines.append("        nlohmann::json j;")
        for name in model.model_fields:
            lines.append(f'        j["{name}"] = {name};')
        lines.append("        return j;")
        lines.append("    }")
        lines.append("")
        lines.append(
            f"    static {model.__name__} from_json(const nlohmann::json& j) {{"
        )
        lines.append(f"        {model.__name__} obj;")
        for name in model.model_fields:
            lines.append(
                f'        obj.{name} = j.at("{name}").get<decltype(obj.{name})>();'
            )
        lines.append("        return obj;")
        lines.append("    }")
        lines.append("")
        # YAML serialization
        lines.append("    YAML::Node to_yaml() const {")
        lines.append("        YAML::Node node;")
        for name in model.model_fields:
            lines.append(f'        node["{name}"] = {name};')
        lines.append("        return node;")
        lines.append("    }")
        lines.append("")
        lines.append(
            f"    static {model.__name__} from_yaml(const YAML::Node& node) {{"
        )
        lines.append(f"        {model.__name__} obj;")
        for name in model.model_fields:
            lines.append(
                f'        obj.{name} = node["{name}"].as<decltype(obj.{name})>();'
            )
        lines.append("        return obj;")
        lines.append("    }")
        lines.append("")
        # XML serialization
        lines.append("    std::string to_xml() const {")
        lines.append("        rapidxml::xml_document<> doc;")
        lines.append(
            f'        auto* root = doc.allocate_node(rapidxml::node_element, "{model.__name__}");'
        )
        lines.append("        doc.append_node(root);")
        for name, field in model.model_fields.items():
            annotation = field.annotation
            lines.append("        {")
            lines.append(
                f'            auto* node = doc.allocate_node(rapidxml::node_element, "{name}");'
            )
            # Use annotation to determine if this is a string field
            if annotation is str:
                lines.append(
                    f"            node->value(doc.allocate_string({name}.c_str()));"
                )
            else:
                lines.append(
                    f"            node->value(doc.allocate_string(std::to_string({name}).c_str()));"
                )
            lines.append("            root->append_node(node);")
            lines.append("        }")
        lines.append(
            "        std::string xml_string; rapidxml::print(std::back_inserter(xml_string), doc, 0);"
        )
        lines.append("        return xml_string;")
        lines.append("    }")
        lines.append("")
        lines.append(
            f"    static {model.__name__} from_xml(const std::string& xml_str) {{"
        )
        lines.append(f"        {model.__name__} obj;")
        lines.append("        rapidxml::xml_document<> doc;")
        lines.append(
            "        std::vector<char> xml_copy(xml_str.begin(), xml_str.end());"
        )
        lines.append("        xml_copy.push_back('\\0');")
        lines.append("        doc.parse<0>(&xml_copy[0]);")
        lines.append(
            f'        auto* root = doc.first_node("{model.__name__}");'
        )
        for name, field in model.model_fields.items():
            annotation = field.annotation
            # Use annotation to determine deserialization logic
            if annotation is str:
                lines.append(
                    f'        if (auto* node = root->first_node("{name}")) obj.{name} = node->value();'
                )
            elif annotation in (int, i8, i16, i32, u8, u16, u32):
                lines.append(
                    f'        if (auto* node = root->first_node("{name}")) obj.{name} = std::stoi(node->value());'
                )
            elif annotation is float:
                lines.append(
                    f'        if (auto* node = root->first_node("{name}")) obj.{name} = std::stod(node->value());'
                )
            else:
                # Fallback: assign as string (safe default for unknown types)
                lines.append(
                    f'        if (auto* node = root->first_node("{name}")) obj.{name} = node->value();'
                )
        lines.append("        return obj;")
        lines.append("    }")
        lines.append("")
        lines.append("};")
        # File I/O helpers
        lines.append("")
        lines.append(
            f"inline void to_json_file(const {model.__name__}& obj, const std::string& path) {{"
        )
        lines.append("    std::ofstream f(path); f << obj.to_json().dump(2); }")
        lines.append(
            f"inline {model.__name__} from_json_file(const std::string& path) {{"
        )
        lines.append(
            f"    std::ifstream f(path); nlohmann::json j; f >> j; return {model.__name__}::from_json(j); }}"
        )
        lines.append("")
        lines.append(
            f"inline void to_yaml_file(const {model.__name__}& obj, const std::string& path) {{"
        )
        lines.append("    std::ofstream f(path); f << obj.to_yaml(); }")
        lines.append(
            f"inline {model.__name__} from_yaml_file(const std::string& path) {{"
        )
        lines.append(
            f"    YAML::Node node = YAML::LoadFile(path); return {model.__name__}::from_yaml(node); }}"
        )
        lines.append("")
        lines.append(
            f"inline void to_xml_file(const {model.__name__}& obj, const std::string& path) {{"
        )
        lines.append("    std::ofstream f(path); f << obj.to_xml(); }")
        lines.append(
            f"inline {model.__name__} from_xml_file(const std::string& path) {{"
        )
        lines.append(
            f"    std::ifstream f(path); std::stringstream buffer; buffer << f.rdbuf(); return {model.__name__}::from_xml(buffer.str()); }}"
        )
        return "\n".join(lines)

    def _cpp_type_str(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)][0]
            return f"std::optional<{self._cpp_type_str(non_none)}>"
        if origin in (list, List):
            return f"std::vector<{self._cpp_type_str(args[0])}>"
        if origin in (dict, Dict):
            return f"std::map<{self._cpp_type_str(args[0])}, {self._cpp_type_str(args[1])}>"
        if annotation is i8:
            return "int8_t"
        if annotation is i16:
            return "int16_t"
        if annotation is i32:
            return "int32_t"
        if annotation is u8:
            return "uint8_t"
        if annotation is u16:
            return "uint16_t"
        if annotation is u32:
            return "uint32_t"
        if annotation is str:
            return "std::string"
        if annotation is float:
            return "double"
        if annotation is int:
            return "int"
        return "auto"
