import os
import re

path_patterns = [
    re.compile(r'^#\s*(.+)$'),
    re.compile(r'^//\s*(.+)$'),
    re.compile(r'^<!--\s*(.+?)\s*-->$'),
]

output_files = []
with open('wersja koncepcyjna', 'r', encoding='utf-8') as f:
    lines = f.readlines()

i = 0
while i < len(lines):
    line = lines[i]
    if line.strip().startswith('```'):
        i += 1
        if i >= len(lines):
            break
        path_line = lines[i].strip()
        path = None
        for pat in path_patterns:
            m = pat.match(path_line)
            if m:
                candidate = m.group(1).strip()
                candidate = re.sub(r'\s*\(.*\)$', '', candidate)
                if ('/' in candidate or '.' in candidate) and not candidate.startswith('http') and ' ' not in candidate:
                    path = candidate
                break
        if path is None:
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            continue
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i].rstrip('\n'))
            i += 1
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as out:
            out.write('\n'.join(code_lines).rstrip() + '\n')
        output_files.append(path)
    else:
        i += 1

print(f'Created {len(output_files)} files.')
