import sys
import hashlib
import math
import platform
import pytest
from pathlib import Path
from datetime import datetime

# Ensure that the C implementation of pickle is not used,
# so that coverage can be calculated correctly
sys.modules["_pickle"] = None

import my_pickle as pickle

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
        filename = path / f"{system}_{py_version}_coverage_results.txt"
        with open(filename, "a", encoding="utf-8") as result_file:
            result_file.write(
                f"Object: {obj}, Protocol: {protocol}, Hash: {hash_value}\n"
            )

# Test of basic types. The latter half of each test case is its opcode
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_none(protocol):
    """Test None"""
    test_cases = [
        (None, [None])
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_bool(protocol):
    """Test bool covering different serialized opcodes"""
    test_cases = [
        (True, ['NEWTRUE']),
        (False, ['NEWFalse'])
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_int(protocol):
    """Test int covering different serialized opcodes"""
    test_cases = [
        (42, ['BININT1']),            # 0–255
        (300, ['BININT2']),           # 256–65535
        (70000, ['BININT']),          # 4 bytes with sign
        (2**32, ['LONG1']),           # long int
        (1 << 2040, ['LONG4'])        # very long int
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_float(protocol):
    """Test float"""
    test_cases = [
        (3.1415926, ['BINFLOAT'])  # All floats use the same opcode
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_bytes(protocol):
    """Test bytes covering different serialized opcodes"""
    test_cases = [
        (b'', ['']),                         # Empty bytes
        (b'short', ['SHORT_BINBYTES']),     # < 256 bytes
        (b'x' * 300, ['BINBYTES']),         # ≥ 256 bytes
        (b'x' * (70 * 1024), ['BINBYTES8']) # Longer than frame size
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_byte_array(protocol):
    """Test bytearray covering different serialized opcodes"""
    test_cases = [
        (bytearray(), ['REDUCE']),                     # Empty bytearray
        (bytearray(b"abc"), ['REDUCE']),               # Short bytearray
        (bytearray(b"x" * 100), ['BYTEARRAY8']),       # Long bytearray
        (bytearray(b"x" * 65536), ['BINBYTES8', '_write_large_bytes'])  # Longer bytearray
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_str(protocol):
    """Test strings covering different serialized opcodes"""
    test_cases = [
        ('ascii', ['SHORT_BINUNICODE']),            # short str
        ('中文字符' * 50, ['BINUNICODE8']),          # long str
        ('', ['SHORT_BINUNICODE'])                   # empty str
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)

            
# test of containers, The latter half of each test case is its opcode
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_list(protocol):
    """Test lists covering different serialized opcodes"""
    test_cases = [
        ([], ['EMPTY_LIST']),                        # Empty list
        ([1, "two", 3.0], ['EMPTY_LIST', 'APPENDS']),  # Short list
        ([[[1, 2], [1, 2]]], ['EMPTY_LIST', 'APPENDS'])  # Nested list
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)
            
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_dict(protocol):
    """Test dicts covering different serialized opcodes"""
    test_cases = [
        ({}, ['EMPTY_DICT']),  # Empty dict
        ({"name": "Alice", "age": 30}, ['EMPTY_LIST', 'SETITEMS']),  # Short dict
        ({"meta": {"version": 2.1}, "data": [1, 2, 3]},
         ['EMPTY_LIST', 'APPENDS', 'EMPTY_DICT', 'TUPLE3']),  # Nested dict
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)
            
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_tuple(protocol):
    """Test tuples covering different serialized opcodes"""
    base_obj = (1, 2, 3, 4)
    test_cases = [
        ((), ['EMPTY_TUPLE']),  # Empty tuple
        ((42,), ['BININT1', 'TUPLE1']),  # Single attribute tuple
        (("a", "b"), ['BINUNICODE', 'BINUNICODE', 'TUPLE2']),  # Two attribute tuple
        ((1.1, 2.2, 3.3), ['BINFLOAT', 'BINFLOAT', 'BINFLOAT', 'TUPLE3']),  # Three attribute tuple
        (tuple(range(100)), ['MARK', 'TUPLE']),  # Big tuple
        (
            (((1.1, 2.2, 3.3), 2.2, 3.3), (1.1, 2.2, 3.3), (1.1, 2.2, 3.3)),
            ['BINFLOAT', 'BINFLOAT', 'BINFLOAT', 'TUPLE3'],
        ),  # Nested tuple
        ((base_obj,), ['TUPLE3']),  # Recursion tuple
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)
            
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_set(protocol):
    """Test sets covering different serialized opcodes"""
    test_cases = [
        (set(), ['EMPTY_SET']),  # empty set
        ({frozenset({1, 2}), "apple"}, ['EMPTY_SET', 'EMPTY_FROZENSET']),  # normal set
        (set(range(2000)), ['EMPTY_SET', 'ADDITEMS']),  # large set
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)
            
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_mixture(protocol):
    """Test mix of containers covering different serialized opcodes"""
    self_ref_list = [1, 2, 3]
    self_ref_list.append(self_ref_list)  # Make the list self-referential

    test_cases = [
        (self_ref_list, ['EMPTY_LIST', 'APPENDS', 'MEMOIZE']),  # self-referential list
        ({"tup": (1,), "set": {1.1, 2.2}}, 
         ['EMPTY_DICT', 'TUPLE1', 'EMPTY_SET', 'ADDITEMS']),  # mix of dict, set, and tuple
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)


# Test of special objects; the latter half of each test case is its opcode
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_global(protocol):
    """Test global objects like functions or dates covering different serialized opcodes"""
    test_cases = [
        (math.sqrt, ['GLOBAL', 'math\nsqrt\n']),                   # global function
        (datetime(2025, 1, 1), ['GLOBAL', 'datetime\ndatetime\n']),  # datetime object
        (datetime.now(), ['GLOBAL', 'datetime\ndatetime\n']),         # current datetime (adaptable)
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)
            
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_type(protocol):
    """Test inner types in Python covering different serialized opcodes"""
    test_cases = [
        (int, ['GLOBAL', 'builtins\nint\n']),          # int
        (float, ['GLOBAL', 'builtins\nfloat\n']),      # float
        (str, ['GLOBAL', 'builtins\nstr\n']),          # str
        (bool, ['GLOBAL', 'builtins\nbool\n']),        # bool
        (type(None), ['REDUCE']),                       # NoneType
        (type(NotImplemented), ['REDUCE']),             # NotImplementedType
        (type(...), ['REDUCE']),                         # EllipsisType
    ]

    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        obj = pickle.loads(bytes_flow)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol=protocol)

        save_test_result(obj, protocol, hash_value)