filepath = r'd:\ОЧ\Програми\Звіт ПБД.html'
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'm3-crew' in line:
        print(f"L{i+1}: {line.strip()}")
