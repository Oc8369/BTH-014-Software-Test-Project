import pickle
import sys
import hashlib
import pytest
import platform


# save the hash result of current system / python
def save_test_result(obj, protocol, hash):
    system = platform.system().lower()
    py_version = f"py{sys.version_info.major}{sys.version_info.minor}"
    filename = f"{system}_{py_version}_all_def_results.txt"
    
    with open(filename, "a") as f:
        f.write(f"Object: {obj}, Protocol: {protocol}, Hash: {hash}\n")
        
@pytest.mark.parametrize("protocol", range(0, 6))        
def test_protocol(protocol):
    '''Verify the all-defs coverage of variable 'protocol' through different protocol versions'''
    test_cases = [
            (None,[None]) 
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        hash = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(0, 6))      
def test_memo(protocol):
    '''Verify the all-defs coverage of variable 'memo' by repeatedly referencing objects'''
    shared_list = [1, 2, 3]
    obj = [shared_list, shared_list]
    
    bytes_flow = pickle.dumps(obj, protocol = protocol)
    assert isinstance(bytes_flow, bytes)
    hash = hashlib.sha256(bytes_flow).hexdigest()
    
    save_test_result(obj, protocol, hash)
    
@pytest.mark.parametrize("protocol", [5])      
def test_farmer(protocol):
    '''Verify the all-defs coverage of variable 'framer' by a byte string exceeding _SRAME-SSIZE_TARGET'''
    obj = b"x" * (100 * 1024)
    
    bytes_flow = pickle.dumps(obj, protocol = protocol)
    assert isinstance(bytes_flow, bytes)
    hash = hashlib.sha256(bytes_flow).hexdigest()
    
    save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", [5])   
def test_buffer_callback(protocol):
    '''Verify the all-defs coverage of variable '_buffer_callback' by Deserialization after serialization'''
    obj = bytearray(b"Test buffer data for pickle")
    
    bytes_flow = pickle.dumps(obj, protocol = protocol)
    assert isinstance(bytes_flow, bytes)
    hash = hashlib.sha256(bytes_flow).hexdigest()
    
    save_test_result(obj, protocol, hash)
 
@pytest.mark.parametrize("protocol", range(0, 6))     
def test_dispatch(protocol):
    '''Verify the all-defs coverage of variable 'dispatch' by dump all data types in it'''
    test_cases = [
        # basic type
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
        
        # container
        [1, 2, 3],
        (1, 2, 3),
        {"a": 1, "b": 2},
        set([1, 2, 3]),
        frozenset([4, 5, 6]),
        
        # special obj
        range(10),
        slice(1, 10, 2),
        ...,
        NotImplemented,
        
        # function and class
        object(),
    ]
    for obj in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        hash = hashlib.sha256(bytes_flow).hexdigest()
    
        save_test_result(obj, protocol, hash)
