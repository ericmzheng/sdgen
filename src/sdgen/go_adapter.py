from typing import List, Union, get_args, get_origin

from .language_adapter import LanguageAdapter
from .model import i8, i16, i32, u8, u16, u32


class GoLanguageAdapter(LanguageAdapter):
    def generate_definition(self) -> str:
        """
        Generate a Go struct definition and serialization/deserialization code for JSON and XML.
        """
        model = self.model._model()
        lines = [
            'import (',
            '    "encoding/json"',
            '    "encoding/xml"',
            '    "gopkg.in/yaml.v3"',
            ')',
            '',
            f'type {model.__name__} struct {{'
        ]
        for name, field in model.model_fields.items():
            annotation = field.annotation
            type_str = self._go_type_str(annotation)
            # Capitalize field name for Go export
            go_field_name = name[:1].upper() + name[1:]
            lines.append(f'    {go_field_name} {type_str} `json:"{name}" xml:"{name}" yaml:"{name}"`')
        lines.append('}')
        lines.append('')
        # JSON serialization
        lines.append(f'func (m *{model.__name__}) ToJSON() (string, error) {{')
        lines.append('    b, err := json.MarshalIndent(m, "", "  ")')
        lines.append('    return string(b), err')
        lines.append('}')
        lines.append('')
        lines.append(f'func {model.__name__}FromJSON(data string) (*{model.__name__}, error) {{')
        lines.append(f'    var m {model.__name__}')
        lines.append('    err := json.Unmarshal([]byte(data), &m)')
        lines.append('    return &m, err')
        lines.append('}')
        lines.append('')
        # XML serialization
        lines.append(f'func (m *{model.__name__}) ToXML() (string, error) {{')
        lines.append('    b, err := xml.MarshalIndent(m, "", "  ")')
        lines.append('    return string(b), err')
        lines.append('}')
        lines.append('')
        lines.append(f'func {model.__name__}FromXML(data string) (*{model.__name__}, error) {{')
        lines.append(f'    var m {model.__name__}')
        lines.append('    err := xml.Unmarshal([]byte(data), &m)')
        lines.append('    return &m, err')
        lines.append('}')
        lines.append('')
        # YAML serialization
        lines.append(f'func (m *{model.__name__}) ToYAML() (string, error) {{')
        lines.append('    b, err := yaml.Marshal(m)')
        lines.append('    return string(b), err')
        lines.append('}')
        lines.append('')
        lines.append(f'func {model.__name__}FromYAML(data string) (*{model.__name__}, error) {{')
        lines.append(f'    var m {model.__name__}')
        lines.append('    err := yaml.Unmarshal([]byte(data), &m)')
        lines.append('    return &m, err')
        lines.append('}')
        return "\n".join(lines)

    def _go_type_str(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)][0]
            return f"*{self._go_type_str(non_none)}"
        if origin in (list, List):
            return f"[]{self._go_type_str(args[0])}"
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
            return "float64"
        if annotation is str:
            return "string"
        return "interface{}"
