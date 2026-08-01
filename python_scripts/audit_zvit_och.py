import re

filepath = r'd:\ОЧ\Програми\Звіт ОЧ.html'
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

full_text = "".join(lines)

# 1. External scripts
ext_scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', full_text)
print("External scripts:", ext_scripts)

# 2. Inline scripts
inline_scripts = re.findall(r'<script>(.*?)</script>', full_text, re.DOTALL)
print(f"Inline script blocks: {len(inline_scripts)}")

# 3. Check element IDs defined in HTML vs referenced in JS
html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', full_text))

js_get_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', full_text))
js_query_ids = set(re.findall(r'querySelector\(["\']#([^"\']+)["\']\)', full_text))
js_used_ids = js_get_ids.union(js_query_ids)

missing_in_html = js_used_ids - html_ids
print("JS references IDs not found in HTML:", missing_in_html)

# 4. Check inline onclick / onchange handlers
inline_handlers = re.findall(r'on[a-z]+=["\']([^"\']+)["\']', full_text)
print(f"Inline handlers count: {len(inline_handlers)}")

# 5. Check function definitions vs calls
func_defs = set(re.findall(r'function ([a-zA-Z0-9_]+)\(', full_text))
print(f"JS functions count: {len(func_defs)}")

# Check any window / document event listeners
listeners = re.findall(r'addEventListener\(["\']([^"\']+)["\']', full_text)
print("Event listeners:", set(listeners))
