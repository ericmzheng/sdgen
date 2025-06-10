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


class RustLanguageAdapter(LanguageAdapter):
    def generate_definition(self) -> str:
        model = self.model._model()
        lines = [
            f"#[derive(Debug, serde::Serialize, serde::Deserialize, PartialEq, Clone)]\npub struct {model.__name__} {{"
        ]
        for name, field in model.model_fields.items():
            annotation = field.annotation
            type_str = self._rust_type_str(annotation)
            lines.append(f"    pub {name}: {type_str},")
        lines.append("}")
        lines.append(f"\nimpl {model.__name__} {{")
        lines.append(
            "    pub fn to_json(&self) -> String { serde_json::to_string_pretty(self).unwrap() }"
        )
        lines.append(
            "    pub fn from_json(s: &str) -> Self { serde_json::from_str(s).unwrap() }"
        )
        lines.append(
            "    pub fn to_yaml(&self) -> String { serde_yaml::to_string(self).unwrap() }"
        )
        lines.append(
            "    pub fn from_yaml(s: &str) -> Self { serde_yaml::from_str(s).unwrap() }"
        )
        lines.append(
            "    pub fn to_xml(&self) -> String { serde_xml_rs::to_string(self).unwrap() }"
        )
        lines.append(
            "    pub fn from_xml(s: &str) -> Self { serde_xml_rs::from_str(s).unwrap() }"
        )
        lines.append("}")
        return "\n".join(lines)

    def _rust_type_str(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)][0]
            return f"Option<{self._rust_type_str(non_none)}>"
        if origin in (list, List):
            return f"Vec<{self._rust_type_str(args[0])}>"
        if origin in (dict, Dict):
            return f"std::collections::HashMap<{self._rust_type_str(args[0])}, {self._rust_type_str(args[1])}>"
        if annotation is i8:
            return "i8"
        if annotation is i16:
            return "i16"
        if annotation is i32:
            return "i32"
        if annotation is u8:
            return "u8"
        if annotation is u16:
            return "u16"
        if annotation is u32:
            return "u32"
        if annotation is str:
            return "String"
        if annotation is float:
            return "f64"
        if annotation is int:
            return "i64"
        return "serde_json::Value"
