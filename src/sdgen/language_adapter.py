from typing import Type

from .model import DataStructureModelClass


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
