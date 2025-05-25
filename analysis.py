import glob
import re
import os
import argparse


def compare_and_save(input_dir: str, output_dir: str, mode: str):
    assert mode in {"python", "system"}, "mode must be either 'python' or 'system'"

    pattern = re.compile(r'^Object: (.*), Protocol: (.*), Hash: (.*)$')
    filepaths = glob.glob(os.path.join(input_dir, "*_results.txt"))

    if not filepaths:
        print(f"[Warning] No *_results.txt files found in {input_dir}.")
        return

    files = [open(fp, 'r', encoding='utf-8', errors='replace') for fp in filepaths]
    os.makedirs(output_dir, exist_ok=True)

    out_path = os.path.join(output_dir, f"hash_differences_{mode}.txt")
    with open(out_path, "w", encoding="utf-8") as out:
        line_number = 1
        while True:
            lines = [f.readline() for f in files]
            if all(line == '' for line in lines):
                break

            parsed = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                match = pattern.match(line)
                if not match:
                    continue

                obj, proto, hval = match.group(1), match.group(2), match.group(3)
                parsed.append((filepaths[i], obj, proto, hval))

            hashes = set(item[3] for item in parsed)
            if len(hashes) > 1:
                obj, proto = parsed[0][1], parsed[0][2]
                out.write(f"--- Difference at line {line_number} ---\n")
                out.write(f"Object: {obj}, Protocol: {proto}\n")
                for fname, _, _, hval in parsed:
                    out.write(f"File: {fname}, Hash: {hval}\n")
                out.write("\n")

            line_number += 1

    for f in files:
        f.close()

    print(f"[Done] Comparison complete. Results saved to {out_path}")
    
def compare_and_save_for_fuzzing(input_dir: str, output_dir: str, mode: str):
    assert mode in {"python", "system"}, "mode must be either 'python' or 'system'"

    pattern = re.compile(r'^Object: (.*), Protocol: (.*), Hash: (.*)$')
    filepaths = glob.glob(os.path.join(input_dir, "*_results.txt"))

    if not filepaths:
        print(f"[Warning] No *_results.txt files found in {input_dir}.")
        return

    files = [open(fp, 'r', encoding='utf-8', errors='replace') for fp in filepaths]
    os.makedirs(output_dir, exist_ok=True)

    out_path = os.path.join(output_dir, f"hash_differences_{mode}.txt")
    with open(out_path, "w", encoding="utf-8") as out:
        line_number = 1
        while True:
            lines = [f.readline() for f in files]
            if all(line == '' for line in lines):
                break

            parsed = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                match = pattern.match(line)
                if not match:
                    continue

                obj, proto, hval = match.group(1), match.group(2), match.group(3)
                parsed.append((filepaths[i], obj, proto, hval))
                
            obj_proto_set = {(item[1], item[2]) for item in parsed}
            if len(obj_proto_set) > 1:
                line_number += 1
                continue    

            hashes = set(item[3] for item in parsed)
            if len(hashes) > 1:
                obj, proto = parsed[0][1], parsed[0][2]
                out.write(f"--- Difference at line {line_number} ---\n")
                out.write(f"Object: {obj}, Protocol: {proto}\n")
                for fname, _, _, hval in parsed:
                    out.write(f"File: {fname}, Hash: {hval}\n")
                out.write("\n")

            line_number += 1

    for f in files:
        f.close()

    print(f"[Done] Comparison complete. Results saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Unified analysis of hash differences in the result directory."
    )
    parser.add_argument(
        "input_dir",
        help="Path to input directory, e.g., blackbox_test/boundary_test/result_different_python_version"
    )
    parser.add_argument(
        "output_base",
        help="Base path to output results, e.g., analysis_res/"
    )
    parser.add_argument(
        "mode",
        choices=["python", "system"],
        help="Analysis type: 'python' or 'system'"
    )

    args = parser.parse_args()

    # Get module name, e.g., boundary_test, ECP, state_machine
    module_name = os.path.basename(os.path.dirname(args.input_dir.rstrip("/")))
    output_dir = os.path.join(args.output_base, module_name)

    # check if "fuzzing" and use different function
    if "fuzzing" in args.input_dir.replace("\\", "/").lower():
        compare_and_save_for_fuzzing(args.input_dir, output_dir, args.mode)
    else:
        compare_and_save(args.input_dir, output_dir, args.mode)
