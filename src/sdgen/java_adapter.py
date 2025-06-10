from typing import List, Union, get_args, get_origin

from pydantic import BaseModel

from .language_adapter import LanguageAdapter
from .model import (
    i8,
    i16,
    i32,
    u8,
    u16,
    u32,
)


class JavaLanguageAdapter(LanguageAdapter):
    def generate_definition(self) -> str:
        model = self.model._model()
        lines = [
            "import com.fasterxml.jackson.annotation.*;",
            "import com.fasterxml.jackson.databind.*;",
            "import com.fasterxml.jackson.dataformat.yaml.*;",
            "import com.fasterxml.jackson.dataformat.xml.annotation.*;",
            "import javax.xml.bind.annotation.*;",
            "import java.util.*;",
            "",
            f'@XmlRootElement(name="{model.__name__}")',
            f"public class {model.__name__} {{",
        ]
        for name, field in model.model_fields.items():
            annotation = field.annotation
            java_type = self._java_type_str(annotation)
            lines.append(f'    @JsonProperty("{name}")')
            lines.append(f'    @XmlElement(name="{name}")')
            lines.append(f"    public {java_type} {name};")
        lines.append("")
        lines.append(f"    public {model.__name__}() {{}}")
        args = ", ".join(
            f"{self._java_type_str(f.annotation)} {n}"
            for n, f in model.model_fields.items()
        )
        lines.append(f"    public {model.__name__}({args}) {{")
        for n in model.model_fields:
            lines.append(f"        this.{n} = {n};")
        lines.append("    }")
        lines.append("")
        lines.append("    @Override public String toString() {")
        lines.append(
            f'        return "{model.__name__}('
            + ", ".join([f'{n}=" + {n} + "' for n in model.model_fields])
            + ')";'
        )
        lines.append("    }")
        # Serialization/Deserialization methods
        lines.append("")
        lines.append("    public String toJson() throws Exception {")
        lines.append(
            "        return new ObjectMapper().writeValueAsString(this);"
        )
        lines.append("    }")
        lines.append("")
        lines.append(
            f"    public static {model.__name__} fromJson(String json) throws Exception {{"
        )
        lines.append(
            f"        return new ObjectMapper().readValue(json, {model.__name__}.class);"
        )
        lines.append("    }")
        lines.append("")
        lines.append("    public String toYaml() throws Exception {")
        lines.append(
            "        return new ObjectMapper(new YAMLFactory()).writeValueAsString(this);"
        )
        lines.append("    }")
        lines.append("")
        lines.append(
            f"    public static {model.__name__} fromYaml(String yaml) throws Exception {{"
        )
        lines.append(
            f"        return new ObjectMapper(new YAMLFactory()).readValue(yaml, {model.__name__}.class);"
        )
        lines.append("    }")
        lines.append("")
        lines.append("    public String toXml() throws Exception {")
        lines.append(
            "        java.io.StringWriter sw = new java.io.StringWriter();"
        )
        lines.append(
            f"        javax.xml.bind.JAXBContext ctx = javax.xml.bind.JAXBContext.newInstance({model.__name__}.class);"
        )
        lines.append(
            "        javax.xml.bind.Marshaller m = ctx.createMarshaller();"
        )
        lines.append(
            "        m.setProperty(javax.xml.bind.Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);"
        )
        lines.append("        m.marshal(this, sw);")
        lines.append("        return sw.toString();")
        lines.append("    }")
        lines.append("")
        lines.append(
            f"    public static {model.__name__} fromXml(String xml) throws Exception {{"
        )
        lines.append(
            f"        javax.xml.bind.JAXBContext ctx = javax.xml.bind.JAXBContext.newInstance({model.__name__}.class);"
        )
        lines.append(
            "        javax.xml.bind.Unmarshaller um = ctx.createUnmarshaller();"
        )
        lines.append(
            "        return ({0}) um.unmarshal(new java.io.StringReader(xml));".format(
                model.__name__
            )
        )
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines)

    def _java_type_str(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)][0]
            return self._java_type_str(non_none)
        if origin in (list, List):
            return f"List<{self._java_type_str(args[0])}>"
        if annotation is str:
            return "String"
        if annotation is int:
            return "int"
        if annotation is (i8, i16, i32, u8, u16, u32):
            return "int"
        if annotation is str:
            return "String"
        if annotation is float:
            return "double"
        if annotation is bool:
            return "boolean"
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return annotation.__name__
        return "Object"
