from typing import List, Union, get_args, get_origin

from .language_adapter import LanguageAdapter
from .model import i8, i16, i32, u8, u16, u32


class CsLanguageAdapter(LanguageAdapter):
    def generate_definition(self) -> str:
        """
        Generate a C# class definition and serialization/deserialization code for JSON and XML.
        """
        model = self.model._model()
        lines = [
            "using System;",
            "using System.Text.Json;",
            "using System.Text.Json.Serialization;",
            "using System.Xml.Serialization;",
            "",
            f"public class {model.__name__}",
            "{",
        ]
        for name, field in model.model_fields.items():
            annotation = field.annotation
            type_str = self._cs_type_str(annotation)
            lines.append(
                f"    public {type_str} {name} {{ get; set; }}"
            )
        lines.append("")
        # JSON serialization
        lines.append(
            "    public string ToJson() => JsonSerializer.Serialize(this, new JsonSerializerOptions { WriteIndented = true });"
        )
        lines.append(
            f"    public static {model.__name__} FromJson(string json) => JsonSerializer.Deserialize<{model.__name__}>(json);"
        )
        # XML serialization
        lines.append(
            f"    public string ToXml() {{ using var sw = new System.IO.StringWriter(); new XmlSerializer(typeof({model.__name__})).Serialize(sw, this); return sw.ToString(); }}"
        )
        lines.append(
            f"    public static {model.__name__} FromXml(string xml) {{ using var sr = new System.IO.StringReader(xml); return ({model.__name__})new XmlSerializer(typeof({model.__name__})).Deserialize(sr); }}"
        )
        lines.append("}")
        return "\n".join(lines)

    def _cs_type_str(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)][0]
            return f"{self._cs_type_str(non_none)}?"
        if origin in (list, List):
            return f"List<{self._cs_type_str(args[0])}>"
        if (
            annotation is i8
            or annotation is i16
            or annotation is i32
            or annotation is int
        ):
            return "int"
        if annotation is u8 or annotation is u16 or annotation is u32:
            return "uint"
        if annotation is float:
            return "double"
        if annotation is str:
            return "string"
        return "object"
