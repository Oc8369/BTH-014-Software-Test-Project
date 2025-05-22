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

# Close all files
for f in files:
    f.close()

print("Comparison completed, differences saved in hash_differences.txt")
