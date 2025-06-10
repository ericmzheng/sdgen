from __future__ import annotations

import functools
import json
import os
from typing import Any, Dict, List, Type, Union, get_args, get_origin
from xml.etree.ElementTree import (
    Element,
    SubElement,
    fromstring,
    parse,
    register_namespace,
    tostring,
)

import yaml
from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler, create_model
from pydantic_core import core_schema

from .utils import (
    is_list_type,
    is_optional_type,
    unwrap_list,
    unwrap_optional,
)


class _sdgenint(int):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ):
        def validate(value):
            v = int(value)
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

    @classmethod
    def to_xsd(cls) -> str:
        """
        Generate an XML Schema Definition (XSD) string for the model's schema,
        including nested models and lists.
        """
        model = cls._model()
        XS_NS = "http://www.w3.org/2001/XMLSchema"
        register_namespace("xs", XS_NS)
        schema = Element(f"{{{XS_NS}}}schema")
        # Top-level element
        SubElement(
            schema,
            f"{{{XS_NS}}}element",
            name=model.__name__,
            type=f"{model.__name__}Type",
        )
        complex_types = {}

        def process_model(m):
            if m.__name__ in complex_types:
                return  # Already processed
            ct = Element(f"{{{XS_NS}}}complexType", name=f"{m.__name__}Type")
            seq = SubElement(ct, f"{{{XS_NS}}}sequence")
            for name, field in m.model_fields.items():
                annotation = field.annotation
                if is_optional_type(annotation):
                    annotation = unwrap_optional(annotation)
                if is_list_type(annotation):
                    item_type = unwrap_list(annotation)
                    if isinstance(item_type, type) and issubclass(
                        item_type, BaseModel
                    ):
                        process_model(item_type)
                        SubElement(
                            seq,
                            f"{{{XS_NS}}}element",
                            name=name,
                            type=f"{item_type.__name__}Type",
                            minOccurs="0",
                            maxOccurs="unbounded",
                        )
                    else:
                        xsd_type = _pytype_to_xsd(item_type)
                        SubElement(
                            seq,
                            f"{{{XS_NS}}}element",
                            name=name,
                            type=xsd_type,
                            minOccurs="0",
                            maxOccurs="unbounded",
                        )
                elif isinstance(annotation, type) and issubclass(
                    annotation, BaseModel
                ):
                    process_model(annotation)
                    SubElement(
                        seq,
                        f"{{{XS_NS}}}element",
                        name=name,
                        type=f"{annotation.__name__}Type",
                        minOccurs="0",
                    )
                else:
                    xsd_type = _pytype_to_xsd(annotation)
                    SubElement(
                        seq,
                        f"{{{XS_NS}}}element",
                        name=name,
                        type=xsd_type,
                        minOccurs="0",
                    )
            complex_types[m.__name__] = ct

        def _pytype_to_xsd(annotation):
            if annotation in (int, i8, i16, i32, u8, u16, u32):
                return "xs:int"
            elif annotation is float:
                return "xs:double"
            elif annotation is str:
                return "xs:string"
            else:
                return "xs:string"  # fallback

        process_model(model)
        # Add all complex types in dependency order (outermost last)
        for ct in complex_types.values():
            schema.append(ct)
        return tostring(schema, encoding="unicode", xml_declaration=True)


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
