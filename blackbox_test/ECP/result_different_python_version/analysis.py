import glob
import re

# 正则匹配：提取 Object, Protocol, Hash
pattern = re.compile(r'^Object: (.*), Protocol: (.*), Hash: (.*)$')

# 获取所有结果文件
filepaths = glob.glob("*_results.txt")

# 尝试用更通用的编码打开所有文件（防乱码）
files = [open(fp, 'r', encoding='utf-8', errors='replace') for fp in filepaths]

with open("hash_differences.txt", "w", encoding="utf-8") as out:
    line_number = 1
    while True:
        lines = [f.readline() for f in files]
        if all(line == '' for line in lines):
            break  # 所有文件读完了

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

        hashes = set(item[3] for item in parsed)
        if len(hashes) > 1:
            # 提取 object 和 protocol（只展示一次）
            obj, proto = parsed[0][1], parsed[0][2]
            out.write(f"--- Difference at line {line_number} ---\n")
            out.write(f"Object: {obj}, Protocol: {proto}\n")
            for fname, _, _, hval in parsed:
                out.write(f"File: {fname}, Hash: {hval}\n")
            out.write("\n")

        line_number += 1

# 关闭所有文件
for f in files:
    f.close()

print("比较完成，差异保存在 hash_differences.txt")
