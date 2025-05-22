import sys
import os
import io
import pickle
import hashlib
import platform
from collections import deque

import numpy as np
import pytest


PICKLE_PROTOCOL = 4  # 测试协议版本
MAX_RECURSION = sys.getrecursionlimit()
MAX_INT = 2 ** 31 - 1  # 32位有符号整数最大值

# --------------------------
# 工具函数
# --------------------------


def create_nested_list(depth):
    """创建指定深度的嵌套列表。"""
    obj = []
    for _ in range(depth):
        obj = [obj]
    return obj


def save_test_result(obj, protocol, hash_result):
    """保存当前系统/Python环境的测试结果哈希值。"""
    system = platform.system().lower()
    py_version = f"py{sys.version_info.major}{sys.version_info.minor}"
    filename = f"{system}_{py_version}_results.txt"

    with open(filename, "a") as f:
        f.write(f"Object: {obj}, Protocol: {protocol}, Hash: {hash_result}\n")


# --------------------------
# 边界测试函数
# --------------------------
@pytest.mark.parametrize(
    "obj",
    [
        # 整数 ON / IN / OUT / OFF 点
        2 ** 31 - 1,
        2 ** 31 - 2,
        0,
        2 ** 31,
        -2 ** 31 - 1,
        # 浮点 ON / IN / OUT / OFF 点
        np.finfo(np.float32).max,
        0,
        2 * np.finfo(np.float32).max,
        -np.finfo(np.float32).max,
        # 字符串 ON / IN / OUT / OFF 点
        "a" * 1024,
        "a",
        "a" * 1024,
        "",
    ],
)
def test_primitive_boundaries(obj):
    """基础类型边界值验证。"""
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    assert isinstance(bytes_flow, bytes)

    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    save_test_result(obj, PICKLE_PROTOCOL, hash_result)


@pytest.mark.parametrize(
    "size",
    [
        # 容器递归深度 ON / IN / OUT / OFF 点
        1,
        2,
        0,
        10000,
    ],
)
def test_container_recursion(size):
    """嵌套容器递归深度测试。"""
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
        # 容器大小的 ON / IN / OUT / OFF 点
        1,
        2,
        0,
        10 ** 6,
        2 ** 63 - 1,
    ],
)
def test_large_containers(size):
    """容器容量边界值验证。"""
    if size > 2 ** 63 - 2:
        pytest.skip()
    obj = [i for i in range(size)]
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    assert isinstance(bytes_flow, bytes)
    save_test_result(obj, PICKLE_PROTOCOL, hash_result)


class VersionedClass:
    """用于测试版本兼容的类。"""

    def __init__(self, version):
        self.version = version
        try:
            self.data = list(range(version))
        except TypeError:
            raise TypeError("版本号必须是整数")

    def __getstate__(self):
        return (self.version, self.data)

    def __setstate__(self, state):
        self.version, self.data = state


@pytest.mark.parametrize(
    "version",
    [
        # 类实例状态的 ON / IN / OUT / OFF 点
        0,
        100,
        "invalid",
        2 ** 15,
    ],
)
def test_class_serialization(version):
    """类实例状态序列化验证。"""
    try:
        obj = VersionedClass(version)
        bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
        hash_result = hashlib.sha256(bytes_flow).hexdigest()
        assert isinstance(bytes_flow, bytes)
        save_test_result(obj, PICKLE_PROTOCOL, hash_result)
    except TypeError as e:
        if version == "invalid":  # 预期字符串参数会触发TypeError
            assert "必须是整数" in str(e)


@pytest.mark.parametrize(
    "obj",
    [
        # Unicode 的 ON / IN / OUT / OFF 点
        "\u0000",
        "\U0010FFFF",
        "\uD800",
        "\u0000" * 5000,
    ],
)
def test_unicode_handling(obj):
    """Unicode编码处理验证。"""
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
    """安全边界测试。"""
    sys_call = os.system
    target_module = getattr(sys_call, "__module__", "os")
    target_name = sys_call.__name__

    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == target_module and name == target_name:
                raise pickle.UnpicklingError(f"SecurityBlock: {module}.{name}")
            return super().find_class(module, name)

    class MaliciousPayload:
        def __reduce__(self):
            return (os.system, ("echo hacked",))

    malicious_data = pickle.dumps(MaliciousPayload(), protocol=PICKLE_PROTOCOL)

    with pytest.raises(pickle.UnpicklingError) as exc_info:
        RestrictedUnpickler(io.BytesIO(malicious_data)).load()

    assert f"SecurityBlock: {target_module}.{target_name}" in str(exc_info.value)


"""---------新添加的----------"""


@pytest.mark.parametrize(
    "size",
    [
        0,  # ON点: 空bytes
        1,  # IN点: 单字节
        10 ** 6,  # OUT点: 1MB数据
        2 ** 31  # OFF点: 2GB数据（跳过）
    ],
)
def test_bytes_boundaries(size):
    """二进制数据大小边界验证。"""
    if size > 2 ** 28:  # 256MB以上跳过
        pytest.skip("测试数据过大")
    obj = b"\x01" * size
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    hash_result = hashlib.sha256(bytes_flow).hexdigest()
    save_test_result(f"bytes(len={size})", PICKLE_PROTOCOL, hash_result)
    assert isinstance(bytes_flow, bytes)


@pytest.mark.parametrize(
    "maxlen",
    [
        0,  # ON点: 固定长度队列
        10,  # IN点: 常规队列
        None,  # OFF点: 无限队列
        -1  # 无效参数（应触发异常）
    ],
)
def test_deque_serialization(maxlen):
    """双端队列结构验证。"""
    if maxlen == -1:
        with pytest.raises(ValueError):
            deque([], maxlen=maxlen)
        return

    obj = deque([1, 2, 3], maxlen=maxlen)
    bytes_flow = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)
    loaded = pickle.loads(bytes_flow)
    assert loaded.maxlen == obj.maxlen
    assert list(loaded) == list(obj)