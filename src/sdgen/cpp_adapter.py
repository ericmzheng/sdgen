from typing import Dict, List, Union, get_args, get_origin

from .language_adapter import LanguageAdapter
from .model import (
    i8,
    i16,
    i32,
    u8,
    u16,
    u32,
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
