import re

filepath = r'd:\ОЧ\Програми\Звіт ОЧ.html'
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)', text)
print("FUNCTIONS FOUND:")
for f_name, f_args in funcs:
    print(f"- {f_name}({f_args})")
