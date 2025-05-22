import platform
import random
import hashlib
import pickle
from datetime import datetime
import sys
import string


random.seed(123456)


def save_test_result(obj, protocol, hash_value):
    """Custom storage test result method"""
    system = platform.system().lower()
    py_version = f"py{sys.version_info.major}{sys.version_info.minor}"
    filename = f"{system}_{py_version}_fuzzing_results.txt"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(
            f"Object: {obj!r}, Protocol: {protocol}, Hash: {hash_value}\n"
        )


def random_data(depth=0):
    """Generate controlled random nested data structures"""
    if depth > 5:
        return random_primitive()

    type_choice = random.choice([
        'primitive',
        'list',
        'dict',
        'tuple',
        'set',
        'bytes',
        'frozenset'
    ])

    if type_choice == 'primitive':
        return random_primitive()
    elif type_choice == 'list':
        return [random_data(depth + 1) for _ in range(random.randint(1, 3))]
    elif type_choice == 'dict':
        return {
            random_string(): random_data(depth + 1)
            for _ in range(random.randint(0, 3))
        }
    elif type_choice == 'tuple':
        return tuple(
            random_data(depth + 1) for _ in range(random.randint(0, 3))
        )
    elif type_choice == 'set':
        return generate_set(depth)
    elif type_choice == 'bytes':
        length = random.randint(0, 10)
        return bytes([random.randint(0, 255) for _ in range(length)])
    elif type_choice == 'frozenset':
        return frozenset(generate_set(depth))


def generate_set(depth):
    """Generate collection types and automatically filter out non Hashable elements"""
    elements = []
    for _ in range(random.randint(0, 3)):
        try:
            elem = random_data(depth + 1)
            hash(elem)
            elements.append(elem)
        except TypeError:
            continue
    return set(elements)


def random_primitive():
    """Generate random basic type data, including boundary values"""
    choice = random.choice([
        'none', 'bool', 'int', 'float', 'str',
        'date', 'empty_str', 'special_float',
        'large_int', 'complex'
    ])

    if choice == 'none':
        return None
    elif choice == 'bool':
        return random.choice([True, False])
    elif choice == 'int':
        return random.choice([
            0,
            1,
            -1,
            sys.maxsize,
            -sys.maxsize,
            random.randint(-10 ** 18, 10 ** 18)
        ])
    elif choice == 'float':
        return random_float()
    elif choice == 'str':
        return random_string()
    elif choice == 'date':
        return datetime(
            year=random.randint(1900, 2100),
            month=random.randint(1, 12),
            day=random.randint(1, 28)
        )
    elif choice == 'empty_str':
        return ''
    elif choice == 'special_float':
        return random.choice([
            float('nan'),
            float('inf'),
            -float('inf')
        ])
    elif choice == 'large_int':
        return random.choice([10 ** 100, -10 ** 100])
    elif choice == 'complex':
        return complex(random_float(), random_float())


def random_float():
    """Generate random floating-point numbers, including normal and special values"""
    if random.random() < 0.2:
        return random.choice([
            float('nan'),
            float('inf'),
            -float('inf')
        ])
    return random.uniform(-1e50, 1e50)


def random_string():
    """Generate strings containing multilingual characters and special symbols"""
    char_pool = (
        string.printable
        + ''.join(chr(i) for i in range(0x4E00, 0x4E50))  # 中文
        + ''.join(chr(i) for i in range(0x0400, 0x04FF))  # 西里尔字母
        + ''.join(chr(i) for i in range(0x1F600, 0x1F64F))  # Emoji
    )
    return ''.join(
        random.choice(char_pool)
        for _ in range(random.randint(0, 20))
    )


def test_fuzzing(num=100000):
    """Batch generate data and store it using custom methods"""
    for _ in range(num):
        data = random_data()
        protocol = random.randint(0, 5)

        bytes_flow = pickle.dumps(data, protocol=protocol)
        assert isinstance(bytes_flow, bytes)

        hash_value = hashlib.sha256(bytes_flow).hexdigest()
        save_test_result(data, protocol, hash_value)