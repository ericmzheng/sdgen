import pytest

from sdgen import DataStructureModelClass, LanguageAdapter


class DummyModel(DataStructureModelClass):
    pass


class DummyAdapter(LanguageAdapter):
    pass


def test_generate_definition_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_definition()


def test_generate_xml_deserializer_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_xml_deserializer()


def test_generate_json_deserializer_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_json_deserializer()


def test_generate_yaml_deserializer_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_yaml_deserializer()


def test_generate_xml_serializer_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_xml_serializer()


def test_generate_json_serializer_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_json_serializer()


def test_generate_yaml_serializer_not_implemented():
    adapter = DummyAdapter(DummyModel())
    with pytest.raises(NotImplementedError):
        adapter.generate_yaml_serializer()
