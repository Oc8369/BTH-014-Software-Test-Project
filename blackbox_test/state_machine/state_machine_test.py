import os
import pickle
import hashlib
import platform
import sys
import tempfile
from pathlib import Path
from collections import defaultdict

from hypothesis import strategies as st, settings
from hypothesis.stateful import (
    RuleBasedStateMachine,
    rule,
    initialize,
)

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
        filename = path / f"{system}_{py_version}_state_machine_results.txt"
        with open(filename, "a", encoding="utf-8") as result_file:
            result_file.write(
                f"Object: {obj}, Protocol: {protocol}, Hash: {hash_value}\n"
            )

def obj_hash(obj=None, protocol=pickle.HIGHEST_PROTOCOL, b=None):
    """Compute a SHA-256 hash for the given object or byte stream."""
    try:
        if b is not None:
            return hashlib.sha256(b).hexdigest()
        return hashlib.sha256(pickle.dumps(obj, protocol)).hexdigest()
    except Exception as e:
        try:
            error_str = str(e).encode()
            return f"[ERROR_HASH: {hashlib.sha256(error_str).hexdigest()}]"
        except Exception:
            return "[UNHASHABLE_ERROR]"


@settings(max_examples=5, derandomize=True)
class PickleStabilityMachine(RuleBasedStateMachine):

    def __init__(self):
        super().__init__()
        self.obj = None
        self.protocol = pickle.DEFAULT_PROTOCOL
        self.nested_depth = 99
        self.file_cycles = 99
        self.seen_hashes = set()
        self.stats = {
            "equal": defaultdict(int),
            "protocol": defaultdict(int),
            "illegal": defaultdict(int),
        }
        self.current_log = []


    @initialize(
    combo=st.fixed_dictionaries({
        "data": st.recursive(
            base=(
                st.none()
                | st.booleans()
                | st.integers()
                | st.floats(allow_nan=False)
                | st.text()
                | st.binary()
                | st.lists(st.integers())
                | st.dictionaries(st.text(), st.integers())
            ),
            extend=lambda s: (
                st.lists(s, max_size=3)
                | st.dictionaries(st.text(), s)
            ),
            max_leaves=7,
        ),
        "protocol": st.integers(
            min_value=0, max_value=pickle.HIGHEST_PROTOCOL
        ),
        "nested_depth": st.integers(min_value=2, max_value=10),
        "file_cycles": st.integers(min_value=2, max_value=10),
    })
    )
    def init_obj(self, combo):
        self.obj = combo["data"]
        self.protocol = combo["protocol"]
        self.nested_depth = combo["nested_depth"]
        self.file_cycles = combo["file_cycles"]

    @rule()
    def test_valid_and_invalid_paths(self):
        # Initialize serialization
        try:
            main_bytes = pickle.dumps(self.obj, self.protocol)
            h0 = obj_hash(b=main_bytes)
        except Exception as e:
            h0 = f"[UNPICKLABLE: {type(e).__name__}]"
            main_bytes = None

        if h0 in self.seen_hashes:
            return
        self.seen_hashes.add(h0)

        # Clear and print new test case header
        self.current_log.clear()
        self.current_log.append("\n========== New Test Case ==========")
        self.current_log.append(
            f"Original Obj: {repr(self.obj)} | protocol={self.protocol} "
            f"nested_depth={self.nested_depth} "
            f"file_cycles={self.file_cycles}"
        )

        # —— Valid Path Test ——
        combos = {
            "dumps->loads": lambda: pickle.loads(main_bytes),
            "file_roundtrip": lambda: self._file_roundtrip(self.obj),
            "nested_protocols": self._test_nested_protocols,
            "protocol_chain": self._test_protocol_chain,
            "multi_file_roundtrip": self._test_multi_file,
        }
        for name, func in combos.items():
            self._execute_test(name, func)

        # —— Invalid Path Combinations ——
        err_combos = {
            "dumps->load": lambda: pickle.load(main_bytes),
            "dump->loads": self._err_dump_loads,
            "dumps->loads->loads": self._err_nested_loads,
            "load->load": self._err_load_load,
        }
        for name, func in err_combos.items():
            self._execute_invalid(name, func)

        # —— Protocol Version Check ——
        self._check_protocols(main_bytes)

        # Output the log for this test case
        print("\n".join(self.current_log))

    def _execute_test(self, name, test_func):
        try:
            result = test_func()
            b = pickle.dumps(result, self.protocol)
            h = obj_hash(b=b)
            eq = (result == self.obj)

            # Save test results to file
            save_test_result(self.obj, self.protocol, h)

            self.current_log.append(f"{name:<25} hash={h} equal={eq}")
            self.stats["equal"][f"{name}_equal_{eq}"] += 1
        except Exception as e:
            try:
                eh = obj_hash(obj=e)
                msg = (
                    f"{name:<25} ERROR: {type(e).__name__} - {e} "
                    f"(Hash: {eh})"
                )
            except Exception:
                msg = f"{name:<25} ERROR: {type(e).__name__} - {e} (Unhashable)"
            self.current_log.append(msg)
            self.stats["equal"][f"{name}_error_{type(e).__name__}"] += 1

    def _execute_invalid(self, name, test_func):
        try:
            test_func()
            self.current_log.append(
                f"{name:<25} no exception (unexpected)"
            )
            self.stats["illegal"][f"{name}_no_exception"] += 1
        except Exception as e:
            # Only record exception type and message, do not output hash
            msg = f"{name:<25} ERROR: {type(e).__name__} - {e}"
            self.current_log.append(msg)
            self.stats["illegal"][f"{name}_{type(e).__name__}"] += 1

    def _file_roundtrip(self, obj):
        # Simplify file I/O
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            pickle.dump(obj, tmp, protocol=self.protocol)
            name = tmp.name

        with open(name, "rb") as f:
            res = pickle.load(f)

        os.remove(name)
        return res

    # Error combination method
    def _err_dump_loads(self):
        import io
        buf = io.BytesIO()
        pickle.dump(self.obj, buf, protocol=self.protocol)
        pickle.loads(buf)  # Error: passed BytesIO instead of bytes


    def _err_nested_loads(self):
        b1 = pickle.dumps(self.obj, protocol=self.protocol)
        inter = pickle.loads(b1)
        pickle.loads(inter)  # Error: inter is not bytes


    def _err_load_load(self):
        import io
        buf = io.BytesIO(pickle.dumps(self.obj, protocol=self.protocol))
        inner = pickle.load(buf)
        pickle.load(inner)  # Error: inner is not a file


    def _test_nested_protocols(self):
        cur = self.obj
        for _ in range(self.nested_depth):
            cur = pickle.dumps(cur, self.protocol)
        for _ in range(self.nested_depth):
            cur = pickle.loads(cur)
        return cur


    def _test_protocol_chain(self):
        cur = self.obj
        for p in [0, 1, 2, self.protocol]:
            cur = pickle.loads(pickle.dumps(cur, p))
        return cur


    def _test_multi_file(self):
        cur = self.obj
        for _ in range(self.file_cycles):
            cur = self._file_roundtrip(cur)
        return cur


    def _test_circular_ref(self):
        a = []
        a.append([a])
        return a


    def _check_protocols(self, main_bytes):
        self.current_log.append("===== Different Protocol Versions =====")
        proto_hashes = {}

        for p in range(pickle.HIGHEST_PROTOCOL + 1):
            try:
                if p == self.protocol and main_bytes:
                    b = main_bytes
                else:
                    b = pickle.dumps(self.obj, p)

                h = obj_hash(b=b)
                proto_hashes[p] = h
                self.current_log.append(f"proto {p:<2} hash={h}")

            except Exception as e:
                self.current_log.append(
                    f"proto {p:<2} ERROR: {type(e).__name__}"
                )
                self.stats["protocol"][f"p{p}_error"] += 1

        if len(set(proto_hashes.values())) != len(proto_hashes):
            self.current_log.append("Hash Collision Detected")
            self.stats["protocol"]["hash_collision"] += 1


    def teardown(self):
        print("\n===== Valid Path Statistics =====")
        for k, v in sorted(self.stats["equal"].items()):
            print(f"{k:<35}: {v}")

        print("\n===== Protocol Version Statistics =====")
        if not self.stats["protocol"]:
            print("All protocol versions passed testing")
        else:
            for k, v in sorted(self.stats["protocol"].items()):
                print(f"{k:<35}: {v}")

        print("\n===== Invalid Path Statistics =====")
        if not self.stats["illegal"]:
            print("No illegal operations triggered")
        else:
            for k, v in sorted(self.stats["illegal"].items()):
                print(f"{k:<35}: {v}")

TestPickleStability = PickleStabilityMachine.TestCase
