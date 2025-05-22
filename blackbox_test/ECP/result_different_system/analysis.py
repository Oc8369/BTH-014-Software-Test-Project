import glob
import re

# Regex pattern to extract Object, Protocol, and Hash
pattern = re.compile(r'^Object: (.*), Protocol: (.*), Hash: (.*)$')

# Get all result files
filepaths = glob.glob("*_results.txt")

# Open all files with universal encoding to prevent garbled text
files = [open(fp, 'r', encoding='utf-8', errors='replace') for fp in filepaths]

# Open output file for writing differences
with open("hash_differences.txt", "w", encoding="utf-8") as out:
    line_number = 1
    while True:
        # Read one line from each file
        lines = [f.readline() for f in files]
        if all(line == '' for line in lines):
            break  # All files have been fully read

        # Parse lines from different files
        parsed = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            m = pattern.match(line)
            if not m:
                continue
            obj, proto, hval = m.group(1), m.group(2), m.group(3)
            parsed.append((filepaths[i], obj, proto, hval))

        # Check for hash differences
        hashes = set(item[3] for item in parsed)
        if len(hashes) > 1:
            # Extract object and protocol (display once)
            obj, proto = parsed[0][1], parsed[0][2]
            out.write(f"--- Difference at line {line_number} ---\n")
            out.write(f"Object: {obj}, Protocol: {proto}\n")
            # Write file names and their hashes
            for fname, _, _, hval in parsed:
                out.write(f"File: {fname}, Hash: {hval}\n")
            out.write("\n")

        line_number += 1

# Close all input files
for f in files:
    f.close()

print("Comparison completed. Differences saved in hash_differences.txt")