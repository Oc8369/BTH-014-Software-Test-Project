import pickle
import pytest
import hashlib
import sys
import enum
import datetime
import platform
from pathlib import Path
from collections import deque


# Utilities
def save_test_result(obj, protocol, hash_value):
    """Save test results with object, protocol and hash information.
    
    Results are saved in different directories based on system and Python version.
    """
    system = platform.system().lower()
    py_version = f"py{sys.version_info.major}{sys.version_info.minor}"
    
    base_dir = Path(__file__).parent
    save_paths = []
    
    # Determine save paths based on system and Python version
    if system != "windows":
        save_paths.append(base_dir / "result_different_system_version")
    else:
        if py_version != "py312":
            save_paths.append(base_dir / "result_different_python_version")
        else:
            save_paths.append(base_dir / "result_different_system_version")
            save_paths.append(base_dir / "result_different_python_version")
            
    # Save results to all applicable paths
    for path in save_paths:
        path.mkdir(exist_ok=True)
        filename = path / f"{system}_{py_version}_ecp_results.txt"
        with open(filename, "a", encoding="utf-8") as result_file:
            result_file.write(
                f"Object: {obj}, Protocol: {protocol}, Hash: {hash_value}\n"
            )


def create_recursive_dict():
    """Create recursive dictionary"""
    d = {}
    d['self'] = d
    return d


class CustomClass:
    """Custom classes for testing"""

    def __init__(self, value):
        self.value = value


class NestedClass:

    def __init__(self, value):
        self.value = value


class CyclicClass:

    def __init__(self):
        self.other = None


class SlotsClass:

    __slots__ = ['a', 'b']

    def __init__(self):
        self.a = 1
        self.b = 2


class Color(enum.Enum):

    RED = 1
    GREEN = 2
    BLUE = 3


# tests
@pytest.mark.parametrize("protocol", range(0, 5))
def test_primitive_types(protocol):
    """basic data type"""
    test_cases = [
        ("int", 42),
        ("str", "hello"),
        ("float", 3.14),
        ("bool_true", True),
        ("bool_false", False),
        ("none", None)
    ]

    for _, obj in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        hash = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(obj, protocol, hash)


@pytest.mark.parametrize("protocol", range(0, 5))
def test_containers(protocol):
    """Container type testing"""
    containers = [
        ("list", [1, 2, 3]),
        ("tuple", (4, 5)),
        ("dict", {'b': 2, 'a': 1}),
        ("set", {1, 2, 3}),
        ("frozenset", frozenset([4, 5, 6])),
        ("deque", deque([1, 2, 3])),
        ("bytearray", bytearray(b'abc')),
        ("nested", [{'x': (1, 2)}, {5, 6}, bytearray(b'data')])
    ]

    for _, obj in containers:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        hash = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(obj, protocol, hash)


def create_cyclic_ref():
    obj1 = CyclicClass()
    obj2 = CyclicClass()
    obj1.other = obj2
    obj2.other = obj1
    return obj1


@pytest.mark.parametrize("protocol", [2, 3, 4])
def test_custom_objects(protocol):
    """Custom Object Testing"""
    test_cases = [
        ("simple", CustomClass(5)),
        ("nested", [NestedClass(10), NestedClass(20)]),
        ("cyclic", create_cyclic_ref()),
        ("slots", SlotsClass())
    ]

    for _, obj in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        hash = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(obj, protocol, hash)


@pytest.mark.parametrize("protocol", range(0, 5))
def test_special_types(protocol):
    """Special data type testing"""
    test_cases = [
        ("pathlib", Path("/test/path")),
        ("datetime", datetime.datetime(2023, 1, 1)),
        ("enum", Color.RED),
        ("recursive_dict", create_recursive_dict()),
        ("nan_float", float('nan'))
    ]

    for _, obj in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        hash = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(obj, protocol, hash)