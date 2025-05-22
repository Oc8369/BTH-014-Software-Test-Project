import glob
import re

# Regular expression to extract Object, Protocol, and Hash
pattern = re.compile(r'^Object: (.*), Protocol: (.*), Hash: (.*)$')

# Get all result files
filepaths = glob.glob("*_results.txt")

# Open all files using a general encoding to avoid encoding errors
files = [open(fp, 'r', encoding='utf-8', errors='replace') for fp in filepaths]

with open("hash_differences.txt", "w", encoding="utf-8") as out:
    line_number = 1
    total_matching = 0
    hash_mismatches = 0
    while True:
        lines = [f.readline() for f in files]
        if all(line == '' for line in lines):
            break  # All files have been read

        parsed = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            match = pattern.match(line)
            if not match:
                continue

            obj = match.group(1)
            proto = match.group(2)
            hval = match.group(3)
            parsed.append((filepaths[i], obj, proto, hval))

        if not parsed:
            line_number += 1
            continue

        obj_proto_set = {(item[1], item[2]) for item in parsed}
        if len(obj_proto_set) > 1:
            line_number += 1
            continue

        total_matching += 1
        hashes = set(item[3] for item in parsed)
        if len(hashes) > 1:
            # Extract object and protocol (only display once)
            obj, proto = parsed[0][1], parsed[0][2]
            out.write(f"--- Difference at line {line_number} ---\n")
            out.write(f"Object: {obj}, Protocol: {proto}\n")
            for fname, _, _, hval in parsed:
                out.write(f"File: {fname}, Hash: {hval}\n")
            out.write("\n")

        line_number += 1

    # Write statistical results
    out.write("\n=== Statistical results ===\n")
    out.write(f"Effective comparison of data volume: {total_matching}\n")
    out.write(f"Number of hash inconsistencies: {hash_mismatches}\n")
    if total_matching:
        out.write(
            f"Inconsistency rate: {hash_mismatches / total_matching:.2%}"
        )
    else:
        out.write("No valid comparison data available")

# Close all files
for f in files:
    f.close()

print("Comparison completed，differences are saved in hash_differences.txt")
print(
    f"[Statistics] Effective comparison {total_matching}, "
    f"discovering Differences {hash_mismatches}"
)