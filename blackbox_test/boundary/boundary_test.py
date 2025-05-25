import io
import os
import pickle
import platform
import sys
from collections import deque
from pathlib import Path

import hashlib
import pytest


PICKLE_PROTOCOL = 4  # Test protocol version


# Utility functions
def create_nested_list(depth):
    """Create a nested list with specified depth."""
    obj = []
    for _ in range(depth):
        obj = [obj]
    return obj


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
        filename = path / f"{system}_{py_version}_boundary_results.txt"
        with open(filename, "a", encoding="utf-8") as result_file:
            result_file.write(
                f"Object: {obj}, Protocol: {protocol}, Hash: {hash_value}\n"
            )



# Boundary test functions
@pytest.mark.parametrize(
    "obj",
    [
        # Integer ON/IN/OUT/OFF points
        2 ** 31 - 1,
        2 ** 31 - 2,
        0,
        2 ** 31,
        -2 ** 31 - 1,
        # Float ON/IN/OUT/OFF points
        # numpy.finfo(numpy.float32).max,
        0,
        # 2 * numpy.finfo(numpy.float32).max,
        # -numpy.finfo(numpy.float32).max,
        # String ON/IN/OUT/OFF points
        "a" * 1024,
        "a",
        "a" * 1024,
        "",
    ],
)
def test_primitive_boundaries(obj):
    """Validate boundary values for primitive types."""
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    assert isinstance(bytes_flow, bytes)

    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    save_test_result(obj, PICKLE_PROTOCOL, hash_result)


@pytest.mark.parametrize(
    "size",
    [
        # Container recursion depth ON/IN/OUT/OFF points
        1,
        2,
        0,
        10000,
    ],
)
def test_container_recursion(size):
    """Test nested container recursion depth."""
    if size > 2 ** 10 - 24:
        pytest.skip()
    obj = create_nested_list(size)
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    assert isinstance(bytes_flow, bytes)
    save_test_result(obj, PICKLE_PROTOCOL, hash_result)


@pytest.mark.parametrize(
    "size",
    [
        # Container size ON/IN/OUT/OFF points
        1,
        2,
        0,
        10 ** 6,
        2 ** 63 - 1,
    ],
)
def test_large_containers(size):
    """Validate boundary values for container capacity."""
    if size > 2 ** 63 - 2:
        pytest.skip()
    obj = [i for i in range(size)]
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    assert isinstance(bytes_flow, bytes)
    save_test_result(obj, PICKLE_PROTOCOL, hash_result)


class VersionedClass:
    """Class for testing version compatibility."""

    def __init__(self, version):
        self.version = version
        try:
            self.data = list(range(version))
        except TypeError:
            raise TypeError("Version number must be an integer")

    def __getstate__(self):
        return (self.version, self.data)

    def __setstate__(self, state):
        self.version, self.data = state


@pytest.mark.parametrize(
    "version",
    [
        # Class instance state ON/IN/OUT/OFF points
        0,
        100,
        "invalid",
        2 ** 15,
    ],
)
def test_class_serialization(version):
    """Validate class instance state serialization."""
    try:
        obj = VersionedClass(version)
        bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
        hash_result = hashlib.sha256(bytes_flow).hexdigest()
        assert isinstance(bytes_flow, bytes)
        save_test_result(obj, PICKLE_PROTOCOL, hash_result)
    except TypeError as e:
        if version == "invalid":  # Expected to raise TypeError for string input
            assert "must be an integer" in str(e)


@pytest.mark.parametrize(
    "obj",
    [
        # Unicode ON/IN/OUT/OFF points
        "\u0000",
        "\U0010FFFF",
        "\uD800",
        "\u0000" * 5000,
    ],
)
def test_unicode_handling(obj):
    """Validate Unicode encoding handling."""
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    assert isinstance(bytes_flow, bytes)
    safe_repr = (
        repr(obj)
        .encode("utf-8", errors="replace")
        .decode("utf-8")
    )
    save_test_result(safe_repr, PICKLE_PROTOCOL, hash_result)


def test_unsafe_deserialization():
    """Security boundary test."""
    sys_call = os.system
    target_module = getattr(sys_call, "__module__", "os")
    target_name = sys_call.__name__

    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == target_module and name == target_name:
                raise pickle.UnpicklingError(
                    f"SecurityBlock: {module}.{name}"
                )
            return super().find_class(module, name)

    class MaliciousPayload:
        def __reduce__(self):
            return (os.system, ("echo hacked",))

    malicious_data = pickle.dumps(
        MaliciousPayload(), protocol=PICKLE_PROTOCOL
    )

    with pytest.raises(pickle.UnpicklingError) as exc_info:
        RestrictedUnpickler(io.BytesIO(malicious_data)).load()

    assert f"SecurityBlock: {target_module}.{target_name}" in str(exc_info.value)


@pytest.mark.parametrize(
    "size",
    [
        0,        # ON point: empty bytes
        1,        # IN point: single byte
        10 ** 6,  # OUT point: 1MB data
        2 ** 31   # OFF point: 2GB data (skipped)
    ],
)
def test_bytes_boundaries(size):
    """Validate binary data size boundaries."""
    if size > 2 ** 28:  # Skip if larger than 256MB
        pytest.skip("Test data too large")
    obj = b"\x01" * size
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    save_test_result(f"bytes(len={size})", PICKLE_PROTOCOL, hash_result)
    assert isinstance(bytes_flow, bytes)


@pytest.mark.parametrize(
    "maxlen",
    [
        0,    # ON point: fixed-length queue
        10,   # IN point: normal queue
        None, # OFF point: infinite queue
        -1    # Invalid parameter (should raise exception)
    ],
)
def test_deque_serialization(maxlen):
    """Validate deque structure serialization."""
    if maxlen == -1:
        with pytest.raises(ValueError):
            deque([], maxlen=maxlen)
        return

    obj = deque([1, 2, 3], maxlen=maxlen)
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    loaded = pickle.loads(bytes_flow)
    
    assert loaded.maxlen == obj.maxlen
    assert list(loaded) == list(obj)