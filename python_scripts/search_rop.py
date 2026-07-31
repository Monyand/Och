import sys

filename = r'd:\ОЧ\Програми\Додаток 6.html'
with open(filename, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    l_lower = line.lower()
    if 'роп' in l_lower or 'vop' in l_lower or 'позиц' in l_lower or 'hierarchy' in l_lower or 'delete' in l_lower or 'видал' in l_lower:
        print(f"L{i+1}: {line.strip()[:120]}")
