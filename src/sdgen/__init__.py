from __future__ import annotations

import functools
import json
import os
from typing import Any, Dict, List, Type, Union, get_args, get_origin
from xml.etree.ElementTree import Element, fromstring, parse, tostring

import yaml  # Add this import at the top
from pydantic import BaseModel, ConfigDict, create_model

__all__ = ["DataStructureModel"]


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

    # --- Deserialization Methods ---

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

            # Handle list types
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
        Deserializes a native Python dictionary into an instance of the model.
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

    # --- Serialization Methods ---

    def to_native_tree(self) -> Dict[str, Any]:
        """
        Serializes the model instance to a native Python dictionary.
        """
        return self.model_dump()

    def to_xml_tree(self) -> Element:
        """
        Serializes the model instance to an XML Element.
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
    def __init__(self, model: DataStructureModelClass):
        self.model = model

    def generate_definition(self) -> str:
        """
        Generate the language-specific data structure definition.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_definition."
        )

    def generate_xml_deserializer(self) -> str:
        """
        Generate the language-specific XML deserialization code.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_xml_deserializer."
        )

    def generate_json_deserializer(self) -> str:
        """
        Generate the language-specific JSON deserialization code.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_json_deserializer."
        )

    def generate_yaml_deserializer(self) -> str:
        """
        Generate the language-specific YAML deserialization code.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_yaml_deserializer."
        )

    def generate_xml_serializer(self) -> str:
        """
        Generate the language-specific XML serialization code.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_xml_serializer."
        )

    def generate_json_serializer(self) -> str:
        """
        Generate the language-specific JSON serialization code.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_json_serializer."
        )

    def generate_yaml_serializer(self) -> str:
        """
        Generate the language-specific YAML serialization code.
        Implementations must override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_yaml_serializer."
        )
