from typing import List, Union, get_args, get_origin

from .language_adapter import LanguageAdapter
from .model import i8, i16, i32, u8, u16, u32


class SwiftLanguageAdapter(LanguageAdapter):
    def generate_definition(self) -> str:
        """
        Generate a Swift struct definition and Codable serialization/deserialization code for JSON and XML.
        """
        model = self.model._model()
        lines = [
            "import Foundation",
            "",
            f"struct {model.__name__}: Codable {{",
        ]
        for name, field in model.model_fields.items():
            annotation = field.annotation
            type_str = self._swift_type_str(annotation)
            lines.append(f"    var {name}: {type_str}")
        lines.append("")
        # JSON serialization
        lines.append("    func toJSON() -> String? {")
        lines.append("        let encoder = JSONEncoder()")
        lines.append("        encoder.outputFormatting = .prettyPrinted")
        lines.append("        if let data = try? encoder.encode(self) {")
        lines.append("            return String(data: data, encoding: .utf8)")
        lines.append("        }")
        lines.append("        return nil")
        lines.append("    }")
        lines.append("    static func fromJSON(_ json: String) -> Self? {")
        lines.append("        let decoder = JSONDecoder()")
        lines.append("        if let data = json.data(using: .utf8) {")
        lines.append(
            "            return try? decoder.decode(Self.self, from: data)"
        )
        lines.append("        }")
        lines.append("        return nil")
        lines.append("    }")
        # XML serialization (placeholder)
        lines.append(
            "    // XML serialization/deserialization would require a third-party library or custom implementation"
        )
        lines.append("}")
        return "\n".join(lines)

    def _swift_type_str(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)][0]
            return f"{self._swift_type_str(non_none)}?"
        if origin in (list, List):
            return f"[{self._swift_type_str(args[0])}]"
        if (
            annotation is i8
            or annotation is i16
            or annotation is i32
            or annotation is int
        ):
            return "Int"
        if annotation is u8 or annotation is u16 or annotation is u32:
            return "UInt"
        if annotation is float:
            return "Double"
        if annotation is str:
            return "String"
        return "Any"
