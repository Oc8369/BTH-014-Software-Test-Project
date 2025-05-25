import pickle
import sys
import hashlib
import pytest
import platform
from pathlib import Path


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
        filename = path / f"{system}_{py_version}_all_defs_results.txt"
        with open(filename, "a", encoding="utf-8") as result_file:
            result_file.write(
                f"Object: {obj}, Protocol: {protocol}, Hash: {hash_value}\n"
            )
        
@pytest.mark.parametrize("protocol", range(0, 6))
def test_protocol(protocol):
    """Verify the all-defs coverage of variable 'protocol' through different protocol versions."""
    test_cases = [
        (None, [None]),
    ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        hash_value = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", range(0, 6))
def test_memo(protocol):
    """Verify the all-defs coverage of variable 'memo' by repeatedly referencing objects."""
    shared_list = [1, 2, 3]
    obj = [shared_list, shared_list]

    bytes_flow = pickle.dumps(obj, protocol=protocol)
    assert isinstance(bytes_flow, bytes)

    hash_value = hashlib.sha256(bytes_flow).hexdigest()

    save_test_result(obj, protocol, hash_value)
    
@pytest.mark.parametrize("protocol", [5])
def test_farmer(protocol):
    """Verify the all-defs coverage of variable 'framer' by a byte string exceeding _SRAME-SSIZE_TARGET."""
    obj = b"x" * (100 * 1024)

    bytes_flow = pickle.dumps(obj, protocol=protocol)
    assert isinstance(bytes_flow, bytes)
    hash_value = hashlib.sha256(bytes_flow).hexdigest()

    save_test_result(obj, protocol, hash_value)

@pytest.mark.parametrize("protocol", [5])
def test_buffer_callback(protocol):
    """Verify the all-defs coverage of variable '_buffer_callback' by deserialization after serialization."""
    obj = bytearray(b"Test buffer data for pickle")

    bytes_flow = pickle.dumps(obj, protocol=protocol)
    assert isinstance(bytes_flow, bytes)
    hash_value = hashlib.sha256(bytes_flow).hexdigest()

    save_test_result(obj, protocol, hash_value)
 
@pytest.mark.parametrize("protocol", range(0, 6))
def test_dispatch(protocol):
    """Verify the all-defs coverage of variable 'dispatch' by dumping all data types in it."""
    test_cases = [
        # basic types
        None,
        True,
        False,
        42,
        3.14,
        10**100,
        b"binary",
        bytearray(b"bytearray"),
        "unicode",
        complex(1, 2),

        # containers
        [1, 2, 3],
        (1, 2, 3),
        {"a": 1, "b": 2},
        set([1, 2, 3]),
        frozenset([4, 5, 6]),

        # special objects
        range(10),
        slice(1, 10, 2),
        ...,
        NotImplemented,

        # function and class
        object(),
    ]
    for obj in test_cases:
        bytes_flow = pickle.dumps(obj, protocol=protocol)
        assert isinstance(bytes_flow, bytes)
        hash_value = hashlib.sha256(bytes_flow).hexdigest()

        save_test_result(obj, protocol, hash_value)

