import hashlib
import sys
sys.modules["_pickle"] = None # Ensure that C_implementation of pickle not be used, so the coverage can be calculated correctly
import my_pickle as pickle
import pytest
import platform
import math
from datetime import datetime

# save the hash result of current system / python
def save_test_result(obj, protocol, hash):
    system = platform.system().lower()
    py_version = f"py{sys.version_info.major}{sys.version_info.minor}"
    filename = f"{system}_{py_version}_coverage_results.txt"
    
    with open(filename, "a") as f:
        f.write(f"Object: {obj}, Protocol: {protocol}, Hash: {hash}\n")

# test of basic types, The latter half of each test case is its opcode
@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_none(protocol):
    '''Test None'''
    test_cases = [
            (None,[None]) 
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol= protocol)
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_bool(protocol):
    '''Test bool covering different serialized opcodes'''
    test_cases = [
            (True,['NEWTRUE']), 
            (False,['NEWFalse']) 
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol= protocol)
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(-1, 6))    
def test_save_int(protocol):
    '''Test int covering different serialized opcodes'''
    test_cases = [
            (42, ['BININT1']),          # 0-255
            (300, ['BININT2']),         # 256-65535
            (70000, ['BININT']),        # 4bytes with symbol
            (2**32, ['LONG1']),         # long int
            (1 << 2040, ['LONG4']),         # very long int
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol= protocol)
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_float(protocol):
    '''Test float'''
    test_cases = [
            (3.1415926, ['BINFLOAT']),   # all float have same opcode
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol= protocol)
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_bytes(protocol):
    '''Test bytes covering different serialized opcodes'''
    test_cases = [
            (b'', ['']),                            # empty bytes
            (b'short', ['SHORT_BINBYTES']),       # <256 bytes
            (b'x'*300, ['BINBYTES']),             # >=256 bytes
            (b'x' * (70 * 1024), ['BINBYTES8']),     # longer bytes, longer than Frame size.
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol= protocol)
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(-1, 6))
def test_save_byte_array(protocol):
    '''Test bytearray covering different serialized opcodes'''
    test_cases = [
            (bytearray(), ['REDUCE']),            # empty bytearray
            (bytearray(b"abc"), ['REDUCE']),       # short bytearray
            (bytearray(b"x" * 100), ['BYTEARRAY8']),      #long bytearray
            (bytearray(b"x" * 65536), ['BINBYTES8','_write_large_bytes']),     # longer bytearray
        ]
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol= protocol)
        save_test_result(obj, protocol, hash)

@pytest.mark.parametrize("protocol", range(-1, 6))        
def test_save_str(protocol):
    '''Test strings covering different serialized opcodes'''
    test_cases = [
            ('ascii',  ['SHORT_BINUNICODE']),     # short str
            ('中文字符'*50,  ['BINUNICODE8']),     # long str
            ('',  ['SHORT_BINUNICODE']),          # empty str
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)

            
# test of containers, The latter half of each test case is its opcode
@pytest.mark.parametrize("protocol", range(-1, 6))        
def test_save_list(protocol):
    '''Test lists covering different serialized opcodes'''
    test_cases = [
            ([],  ['EMPTY_LIST']),     # empty list
            ([1, "two", 3.0],  ['EMPTY_LIST', 'APPENDS']), # short list
            ([[[1,2],[1,2]]],  ['EMPTY_LIST', 'APPENDS']), # Nested List  
                 
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)
            
@pytest.mark.parametrize("protocol", range(-1, 6))        
def test_save_list(protocol):
    '''Test dicts covering different serialized opcodes'''
    test_cases = [
            ({},  ['EMPTY_DICT']),     # empty dict
            ({"name": "Alice", "age": 30},  ['EMPTY_LIST', 'SETITEMS']), # short dict
            ({"meta": {"version": 2.1}, "data": [1,2,3]},  ['EMPTY_LIST', 'APPENDS', 'EMPTY_DICT','TUPLE3']), # Nested dict   
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)
            
@pytest.mark.parametrize("protocol", range(-1, 6))        
def test_save_tuple(protocol):
    '''Test tuples covering different serialized opcodes'''
    obj = (1, 2, 3, 4)
    test_cases = [
            ((),  ['EMPTY_TUPLE']),     # empty tuple
            ((42,),  ['BININT1', 'TUPLE1']), # single attribute tuple
            (("a", "b"),  ['BINUNICODE', 'BINUNICODE', 'TUPLE2']), # two attribute tuple
            ((1.1, 2.2, 3.3), ['BINFLOAT', 'BINFLOAT', 'BINFLOAT', 'TUPLE3']), # three attribute tuple 
            (tuple(range(100)), ['MARK', 'TUPLE']), # big tuple
            ((((1.1, 2.2, 3.3), 2.2, 3.3), (1.1, 2.2, 3.3), (1.1, 2.2, 3.3)), ['BINFLOAT', 'BINFLOAT', 'BINFLOAT', 'TUPLE3']), # nested tuple
            ((obj,), ['TUPLE3']), # recursion tuple
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)
            
@pytest.mark.parametrize("protocol", range(-1, 6))        
def test_save_set(protocol):
    '''Test sets covering different serialized opcodes'''
    test_cases = [
            (set(),  ['EMPTY_SET']),     # empty set
            ({frozenset({1,2}), "apple"},  ['EMPTY_SET', 'EMPTY_FROZENSET']), # normal set
            (set(range(2000)), ['EMPTY_SET', 'ADDITEMS']) # large set
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)
            
@pytest.mark.parametrize("protocol", range(-1, 6))  
def test_save_mixture(protocol):
    '''Test mix of containers covering different serialized opcodes'''
    self_ref_list = [1,2,3]
    test_cases = [
            (self_ref_list.append(self_ref_list),  ['EMPTY_LIST', 'APPENDS', 'MEMOIZE']),     # empty set
            ({ "tup": (1,), "set": {1.1, 2.2}},  ['EMPTY_DICT', 'TUPLE1', 'EMPTY_SET', 'ADDITEMS']), # mix of dict, set and tuple
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)


# test of special objects, The latter half of each test case is its opcode            
@pytest.mark.parametrize("protocol", range(-1, 6))  
def test_save_global(protocol):
    '''Test global objects like functions or date covering different serialized opcodes'''
    test_cases = [
            (math.sqrt,  ['GLOBAL', 'math\nsqrt\n']),                   # global function
            (datetime(2025,1,1),  ['GLOBAL', 'datetime\ndatetime\n']),  # datetime
            (datetime.now(),  ['GLOBAL', 'datetime\ndatetime\n']),      # adaptable datetime
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)
            
@pytest.mark.parametrize("protocol", range(-1, 6))  
def test_save_type(protocol):
    '''Test inner types in python covering different serialized opcodes'''
    test_cases = [
            (int,  ['GLOBAL', 'builtins\nint\n']),     # int
            (float,  ['GLOBAL', 'builtins\nfloat\n']), # float
            (str,  ['GLOBAL', 'builtins\nstr\n']),     # str
            (bool,  ['GLOBAL', 'builtins\nbool\n']),   # bool
            (type(None),  ['REDUCE']),                 # None
            (type(NotImplemented),  ['REDUCE']),       # NotImplemented
            (type(...),  ['REDUCE']),                   # ...    
        ]        
    for obj, _ in test_cases:
        bytes_flow = pickle.dumps(obj, protocol = protocol)
        assert isinstance(bytes_flow, bytes)
        
        obj = pickle.loads(bytes_flow)
        hash = hashlib.sha256(bytes_flow).hexdigest()
        with open("data.pkl", "wb") as f:
            pickle.dump(obj, f, protocol = protocol)
        save_test_result(obj, protocol, hash)

   
    