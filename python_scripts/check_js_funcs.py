filename = r'd:\ОЧ\Програми\Додаток 6.html'
with open(filename, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

import re
matches_onclick = re.findall(r'onclick="([a-zA-Z0-9_]+)\(', content)
matches_onchange = re.findall(r'onchange="([a-zA-Z0-9_]+)\(', content)
matches_func = re.findall(r'function ([a-zA-Z0-9_]+)\(', content)

all_calls = set(matches_onclick + matches_onchange)
all_funcs = set(matches_func)

print("Calls without function definition:")
for c in all_calls:
    if c not in all_funcs and not c.startswith('document'):
        print("  MISSING FUNC:", c)
